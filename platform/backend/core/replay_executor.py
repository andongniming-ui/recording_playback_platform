"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import json
import logging
import time
from typing import Optional

import httpx
from sqlalchemy import func, or_, select, update

from config import settings
import database
from integration.arex_client import ArexClient, ArexClientError
from models.application import Application
from models.compare import CompareRule
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from utils.assertions import assertions_all_passed, evaluate_assertions
from utils.diff import compute_diff
from utils.timezone import now_beijing
from utils.transaction_mapping import apply_transaction_mapping
from core.replay_audit import append_replay_audit_log as _append_replay_audit_log
from core.replay_heartbeat import (
    REPLAY_WORKER_ID as _REPLAY_WORKER_ID,
    replay_job_heartbeat_loop as _replay_job_heartbeat_loop,
    touch_replay_job_heartbeat as _touch_replay_job_heartbeat,
)
from core.replay_result_writer import save_result as _save_result

# Sub-call diff & matching (extracted to utils)
from utils.replay_sub_call_diff import (
    _build_sub_call_diff_pairs,
    _filter_sub_calls_for_strict_check,
    _strict_sub_call_failure,
    _sub_calls_have_diff,
)
# Sub-call fetching & reconstruction (extracted to utils)
from utils.replay_sub_call_fetch import (
    _fetch_replay_sub_calls,
)
# Compare-rule parsing & failure reasons (extracted to utils)
from utils.replay_compare_rules import (
    _apply_header_transforms,
    _build_failure_reason,
    _collect_compare_rule_effects,
    _load_json_value,
    _normalize_mappings,
    _normalize_rule_entries,
)

logger = logging.getLogger(__name__)
# Empirical wait for AREX agent to finish async reporting after replay.
# Configurable via AR_AREX_FLUSH_DELAY_S in .env (default 1.0s).
# Known limitation: under high load, agent may take longer than this to flush,
# causing sub-calls to be silently missed (frontend shows "Agent 未上报").
_AREX_AGENT_FLUSH_DELAY_S: float = settings.arex_flush_delay_s

_ws_connections: dict[int, set] = {}
_ws_connections_lock = asyncio.Lock()


async def register_ws(job_id: int, ws):
    async with _ws_connections_lock:
        _ws_connections.setdefault(job_id, set()).add(ws)


async def unregister_ws(job_id: int, ws):
    async with _ws_connections_lock:
        if job_id in _ws_connections:
            _ws_connections[job_id].discard(ws)


async def _broadcast_progress(job_id: int, data: dict):
    async with _ws_connections_lock:
        conns = set(_ws_connections.get(job_id, set()))
    dead = set()
    for ws in conns:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    if dead:
        async with _ws_connections_lock:
            for ws in dead:
                _ws_connections.get(job_id, set()).discard(ws)


async def run_replay_job(job_id: int):
    """Main entry point: run a replay job from DB state."""
    async with database.async_session_factory() as db:
        result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning("ReplayJob %s not found", job_id)
            return

        results_query = await db.execute(
            select(ReplayResult.test_case_id)
            .where(ReplayResult.job_id == job_id)
            .where(ReplayResult.test_case_id.isnot(None))
        )
        case_ids = list(results_query.scalars().all())

        if not case_ids:
            job.status = "DONE"
            job.total = 0
            await db.commit()
            await _append_replay_audit_log(
                job_id=job_id,
                application_id=job.application_id,
                event_type="job_finished",
                message="回放任务无可执行用例，直接结束",
                detail={"status": "DONE", "total": 0},
            )
            return

        cases_result = await db.execute(select(TestCase).where(TestCase.id.in_(case_ids)))
        cases = cases_result.scalars().all()
        case_map = {case.id: case for case in cases}

        resolved_application_id = job.application_id
        if resolved_application_id is None:
            case_application_ids = {case.application_id for case in cases if case.application_id is not None}
            if len(case_application_ids) == 1:
                resolved_application_id = next(iter(case_application_ids))
                job.application_id = resolved_application_id

        app = None
        target_host = None
        arex_storage_url = settings.arex_storage_url
        transaction_mappings: list[dict] = []
        if resolved_application_id:
            app_result = await db.execute(
                select(Application).where(Application.id == resolved_application_id)
            )
            app = app_result.scalar_one_or_none()
            if app:
                target_host = f"http://{app.ssh_host}:{app.service_port}"
                arex_storage_url = app.arex_storage_url or settings.arex_storage_url
                transaction_mappings = _normalize_mappings(app.transaction_mappings)

        compare_rule_stmt = select(CompareRule).where(CompareRule.is_active.is_(True))
        if resolved_application_id is None:
            compare_rule_stmt = compare_rule_stmt.where(CompareRule.scope == "global")
        else:
            compare_rule_stmt = compare_rule_stmt.where(
                or_(
                    CompareRule.scope == "global",
                    (CompareRule.scope == "app") & (CompareRule.application_id == resolved_application_id),
                )
            )
        compare_rules_result = await db.execute(compare_rule_stmt.order_by(CompareRule.id))
        compare_rules = compare_rules_result.scalars().all()

        job.status = "RUNNING"
        job.total = len(case_ids)
        job.passed = 0
        job.failed = 0
        job.errored = 0
        job.started_at = now_beijing()
        job.finished_at = None
        job.heartbeat_at = job.started_at
        job.worker_id = _REPLAY_WORKER_ID
        await db.commit()

    await _append_replay_audit_log(
        job_id=job_id,
        application_id=resolved_application_id,
        event_type="job_started",
        target_url=target_host,
        message="回放任务开始执行",
        detail={
            "total": len(case_ids),
            "concurrency": job.concurrency,
            "timeout_ms": job.timeout_ms,
            "use_sub_invocation_mocks": job.use_sub_invocation_mocks,
            "fail_on_sub_call_diff": job.fail_on_sub_call_diff,
            "retry_count": job.retry_count,
            "target_host": target_host,
        },
    )

    base_ignore_fields = _load_json_value(
        app.default_ignore_fields if app else None,
        f"application {resolved_application_id} default_ignore_fields",
        default=[],
    )
    if not isinstance(base_ignore_fields, list):
        base_ignore_fields = []

    diff_rules: list[dict] = []
    assertions_config: list[dict] = []

    app_assertions = _load_json_value(
        app.default_assertions if app else None,
        f"application {resolved_application_id} default_assertions",
        default=[],
    )
    assertions_config.extend(_normalize_rule_entries(app_assertions))

    for rule in compare_rules:
        rule_ignore_fields, rule_diff_rules, rule_assertions = _collect_compare_rule_effects(rule)
        base_ignore_fields.extend(rule_ignore_fields)
        diff_rules.extend(rule_diff_rules)
        assertions_config.extend(rule_assertions)

    diff_rules.extend(_normalize_rule_entries(_load_json_value(job.diff_rules, f"replay job {job_id} diff_rules", default=[])))
    assertions_config.extend(_normalize_rule_entries(_load_json_value(job.assertions, f"replay job {job_id} assertions", default=[])))
    base_ignore_fields.extend(_load_json_value(job.ignore_fields, f"replay job {job_id} ignore_fields", default=[]))
    header_transforms = _load_json_value(job.header_transforms, f"replay job {job_id} header_transforms", default=[])

    perf_threshold_ms = job.perf_threshold_ms if job.perf_threshold_ms is not None else (app.default_perf_threshold_ms if app else None)
    delay_ms = max(job.delay_ms or 0, 0)

    # 从 job 读取 target_host 覆盖（在流量放大之前执行，确保顺序正确）
    if job.target_host:
        target_host = job.target_host

    # 流量放大：将每条 case 重复回放 repeat_count 次
    job_repeat_count = max(1, job.repeat_count or 1)
    if job_repeat_count > 1:
        case_ids = case_ids * job_repeat_count
        job.total = len(case_ids)   # keep local variable in sync for broadcasts
        # 更新 total 为实际执行数
        async with database.async_session_factory() as _db:
            _result = await _db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            _job = _result.scalar_one_or_none()
            if _job:
                _job.total = len(case_ids)
                await _db.commit()

    semaphore = asyncio.Semaphore(job.concurrency)
    progress_lock = asyncio.Lock()
    done_count = 0
    passed = 0
    failed = 0
    errored = 0
    job_smart_noise_reduction = job.smart_noise_reduction
    job_retry_count = job.retry_count
    job_fail_on_sub_call_diff = job.fail_on_sub_call_diff
    job_ignore_order = getattr(job, "ignore_order", True)

    http_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0), follow_redirects=True)
    heartbeat_task = asyncio.create_task(_replay_job_heartbeat_loop(job_id))

    async def _run_one(case_id: int):
        nonlocal done_count, passed, failed, errored
        case = case_map.get(case_id)
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=getattr(case, "application_id", resolved_application_id),
            event_type="case_started",
            request_method=getattr(case, "request_method", None),
            request_uri=getattr(case, "request_uri", None),
            transaction_code=getattr(case, "transaction_code", None),
            target_url=(f"{target_host or 'http://localhost:8080'}{getattr(case, 'request_uri', '')}") if case else None,
            message="开始执行回放用例",
        )
        async with semaphore:
            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)
            result = await _execute_single(
                job_id=job_id,
                case_id=case_id,
                case=case,
                target_host=target_host,
                arex_storage_url=arex_storage_url,
                timeout_ms=job.timeout_ms,
                diff_rules=diff_rules,
                base_ignore_fields=base_ignore_fields,
                assertions_config=assertions_config,
                perf_threshold_ms=perf_threshold_ms,
                use_mocks=job.use_sub_invocation_mocks,
                smart_noise_reduction=job_smart_noise_reduction,
                ignore_order=job_ignore_order,
                header_transforms=header_transforms,
                transaction_mappings=transaction_mappings,
                fail_on_sub_call_diff=job_fail_on_sub_call_diff,
                http_client=http_client,
            )
            # P1: 失败重试
            for _attempt in range(job_retry_count):
                if result.status not in ("FAIL", "ERROR", "TIMEOUT"):
                    break
                logger.info(
                    "Replay case %s failed (status=%s), retrying (%d/%d)…",
                    case_id, result.status, _attempt + 1, job_retry_count,
                )
                await _append_replay_audit_log(
                    job_id=job_id,
                    result_id=result.id,
                    test_case_id=case_id,
                    application_id=getattr(case, "application_id", resolved_application_id),
                    event_type="case_retry",
                    request_method=getattr(case, "request_method", None),
                    request_uri=getattr(case, "request_uri", None),
                    transaction_code=getattr(case, "transaction_code", None),
                    message="回放失败后重试",
                    detail={"attempt": _attempt + 1, "max_retry_count": job_retry_count, "status": result.status},
                )
                await asyncio.sleep(0.5)
                result = await _execute_single(
                    job_id=job_id,
                    case_id=case_id,
                    case=case,
                    target_host=target_host,
                    arex_storage_url=arex_storage_url,
                    timeout_ms=job.timeout_ms,
                    diff_rules=diff_rules,
                    base_ignore_fields=base_ignore_fields,
                    assertions_config=assertions_config,
                    perf_threshold_ms=perf_threshold_ms,
                    use_mocks=job.use_sub_invocation_mocks,
                    smart_noise_reduction=job_smart_noise_reduction,
                    ignore_order=job_ignore_order,
                    header_transforms=header_transforms,
                    transaction_mappings=transaction_mappings,
                    fail_on_sub_call_diff=job_fail_on_sub_call_diff,
                    http_client=http_client,
                )

        async with progress_lock:
            done_count += 1
            increment_values = {}
            if result.status == "PASS":
                passed += 1
                increment_values["passed"] = func.coalesce(ReplayJob.passed, 0) + 1
            elif result.status in ("FAIL", "TIMEOUT"):
                failed += 1
                increment_values["failed"] = func.coalesce(ReplayJob.failed, 0) + 1
            else:
                errored += 1
                increment_values["errored"] = func.coalesce(ReplayJob.errored, 0) + 1

            async with database.async_session_factory() as progress_db:
                if increment_values:
                    await progress_db.execute(
                        update(ReplayJob)
                        .where(ReplayJob.id == job_id)
                        .values(**increment_values)
                    )
                    await progress_db.commit()
                job_result = await progress_db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
                progress_job = job_result.scalar_one_or_none()
                if progress_job:
                    passed = progress_job.passed or 0
                    failed = progress_job.failed or 0
                    errored = progress_job.errored or 0

            await _broadcast_progress(
                job_id,
                {
                    "job_id": job_id,
                    "done": done_count,
                    "total": job.total,
                    "passed": passed,
                    "failed": failed,
                    "errored": errored,
                },
            )

    try:
        await asyncio.gather(*[_run_one(case_id) for case_id in case_ids])
    finally:
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass
        await http_client.aclose()

    async with database.async_session_factory() as db:
        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            passed = job.passed or 0
            failed = job.failed or 0
            errored = job.errored or 0
            job.status = "FAILED" if failed > 0 or errored > 0 else "DONE"
            job.finished_at = now_beijing()
            job.heartbeat_at = job.finished_at
            await db.commit()

    await _append_replay_audit_log(
        job_id=job_id,
        application_id=resolved_application_id,
        event_type="job_finished",
        message="回放任务执行完成",
        detail={
            "status": "FAILED" if failed > 0 or errored > 0 else "DONE",
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "done": done_count,
        },
    )

    await _broadcast_progress(
        job_id,
        {
            "job_id": job_id,
            "done": done_count,
            "total": done_count,
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "finished": True,
        },
    )


async def _execute_single(
    job_id: int,
    case_id: int,
    case: Optional[TestCase],
    target_host: Optional[str],
    arex_storage_url: str,
    timeout_ms: int,
    diff_rules,
    base_ignore_fields=None,
    assertions_config=None,
    perf_threshold_ms: Optional[int] = None,
    use_mocks: bool = False,
    smart_noise_reduction: bool = False,
    ignore_order: bool = True,
    header_transforms=None,
    transaction_mappings: list[dict] | None = None,
    fail_on_sub_call_diff: bool = False,
    http_client: Optional[httpx.AsyncClient] = None,
) -> ReplayResult:
    """Execute one test case and save the result back into the placeholder row."""
    application_id = getattr(case, "application_id", None) if case else None
    transaction_code = getattr(case, "transaction_code", None)
    if not case:
        result = await _save_result(
            job_id=job_id,
            case_id=case_id,
            status="ERROR",
            is_pass=False,
            failure_category="connection_error",
            failure_reason="Test case not found",
        )
        await _append_replay_audit_log(
            job_id=job_id,
            result_id=result.id,
            test_case_id=case_id,
            application_id=application_id,
            level="ERROR",
            event_type="case_finished",
            message="回放用例不存在",
            detail={"status": result.status, "failure_category": "connection_error", "failure_reason": "Test case not found"},
        )
        return result

    mock_record_id = None
    replay_arex_record_id = None
    if use_mocks:
        if not case.source_recording_id:
            result = await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="use_sub_invocation_mocks requires a test case created from a recording",
            )
            await _append_replay_audit_log(
                job_id=job_id,
                result_id=result.id,
                test_case_id=case_id,
                application_id=application_id,
                level="ERROR",
                event_type="case_finished",
                request_method=case.request_method,
                request_uri=case.request_uri,
                transaction_code=transaction_code,
                message="缺少源录制，无法加载 mock",
                detail={"status": result.status, "failure_category": "mock_error", "failure_reason": result.failure_reason},
            )
            return result
        async with database.async_session_factory() as db:
            recording_result = await db.execute(
                select(Recording).where(Recording.id == case.source_recording_id)
            )
            recording = recording_result.scalar_one_or_none()
        if not recording or not recording.record_id:
            result = await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="Source recording not found or missing AREX record_id",
            )
            await _append_replay_audit_log(
                job_id=job_id,
                result_id=result.id,
                test_case_id=case_id,
                application_id=application_id,
                level="ERROR",
                event_type="case_finished",
                request_method=case.request_method,
                request_uri=case.request_uri,
                transaction_code=transaction_code,
                message="源录制不存在或缺少 AREX record_id",
                detail={"status": result.status, "failure_category": "mock_error", "failure_reason": result.failure_reason},
            )
            return result
        mock_record_id = recording.record_id

    base_url = target_host or "http://localhost:8080"
    url = f"{base_url}{case.request_uri}"
    ignore_fields = list(base_ignore_fields or [])
    if case.ignore_fields:
        try:
            case_ignore_fields = json.loads(case.ignore_fields)
            if isinstance(case_ignore_fields, list):
                ignore_fields.extend(case_ignore_fields)
        except Exception:
            logger.warning("Replay case %s has invalid ignore_fields JSON", case.id)

    headers = {}
    if case.request_headers:
        try:
            headers = json.loads(case.request_headers)
        except Exception:
            logger.warning("Replay case %s has invalid request_headers JSON", case.id)
    headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in ("host", "content-length")
    }
    headers = _apply_header_transforms(headers, header_transforms)
    mapped_request_body = apply_transaction_mapping(
        case.request_body,
        transaction_code,
        transaction_mappings,
        direction="request",
    )

    start = time.monotonic()
    actual_status = None
    actual_body = None
    status = "ERROR"
    failure_category = None
    failure_reason = None
    mock_client: ArexClient | None = None
    mock_loaded = False
    replay_completed_at_ms = None

    try:
        if use_mocks and mock_record_id:
            mock_client = ArexClient(arex_storage_url)
            await mock_client.__aenter__()
            await mock_client.cache_load_mock(mock_record_id)
            mock_loaded = True
            await _append_replay_audit_log(
                job_id=job_id,
                test_case_id=case_id,
                application_id=application_id,
                event_type="mock_loaded",
                request_method=case.request_method,
                request_uri=case.request_uri,
                transaction_code=transaction_code,
                message="已加载子调用 mock",
                detail={"mock_record_id": mock_record_id},
            )

        timeout = httpx.Timeout(timeout_ms / 1000.0)
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            event_type="request_sent",
            target_url=url,
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            message="已发送回放请求",
            detail={"headers": headers, "request_body": mapped_request_body, "timeout_ms": timeout_ms},
        )
        if http_client is not None:
            resp = await http_client.request(
                method=case.request_method or "GET",
                url=url,
                content=mapped_request_body.encode() if mapped_request_body else None,
                headers=headers,
                timeout=timeout,
            )
        else:
            async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
                resp = await client.request(
                    method=case.request_method or "GET",
                    url=url,
                    content=mapped_request_body.encode() if mapped_request_body else None,
                    headers=headers,
                )
        actual_status = resp.status_code
        actual_body = resp.text
        resp_headers = getattr(resp, "headers", {}) or {}
        replay_arex_record_id = resp_headers.get("arex-record-id") if hasattr(resp_headers, "get") else None
        replay_completed_at_ms = int(time.time() * 1000)
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "OK_GOT_RESPONSE"
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            event_type="response_received",
            target_url=url,
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            actual_status_code=actual_status,
            latency_ms=latency_ms,
            message="已收到回放响应",
            detail={"replay_arex_record_id": replay_arex_record_id, "response_headers": dict(resp_headers) if hasattr(resp_headers, "items") else None},
        )
    except httpx.TimeoutException:
        latency_ms = timeout_ms
        status = "TIMEOUT"
        failure_category = "timeout"
        failure_reason = f"Request timed out after {timeout_ms}ms"
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            level="ERROR",
            event_type="request_timeout",
            target_url=url,
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            latency_ms=latency_ms,
            message="回放请求超时",
            detail={"timeout_ms": timeout_ms},
        )
    except ArexClientError as exc:
        latency_ms = 0
        status = "ERROR"
        failure_category = "mock_error"
        failure_reason = str(exc)
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            level="ERROR",
            event_type="mock_error",
            target_url=url,
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            message="回放 mock 处理失败",
            detail={"error": str(exc)},
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "ERROR"
        failure_category = "connection_error"
        failure_reason = str(exc)
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            level="ERROR",
            event_type="request_error",
            target_url=url,
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            latency_ms=latency_ms,
            message="回放请求执行异常",
            detail={"error": str(exc)},
        )
    finally:
        if mock_loaded and mock_record_id and mock_client is not None:
            try:
                await mock_client.cache_remove_mock(mock_record_id)
                await _append_replay_audit_log(
                    job_id=job_id,
                    test_case_id=case_id,
                    application_id=application_id,
                    event_type="mock_removed",
                    request_method=case.request_method,
                    request_uri=case.request_uri,
                    transaction_code=transaction_code,
                    message="已移除子调用 mock",
                    detail={"mock_record_id": mock_record_id},
                )
            except Exception as exc:
                logger.warning("Failed to remove AREX mock cache for %s: %s", mock_record_id, exc)
        if mock_client is not None:
            await mock_client.aclose()

    diff_json = None
    diff_score = None
    assertion_results_json = None
    is_pass = False
    mapped_actual_body = actual_body

    if status == "OK_GOT_RESPONSE":
        mapped_actual_body = apply_transaction_mapping(
            actual_body,
            transaction_code,
            transaction_mappings,
            direction="response",
        )

        diff_json, diff_score = compute_diff(
            original=case.expected_response,
            replayed=mapped_actual_body,
            diff_rules=diff_rules,
            ignore_fields=ignore_fields,
            smart_noise_reduction=smart_noise_reduction,
            ignore_order=ignore_order,
        )

        combined_assertions = []
        if assertions_config:
            combined_assertions.extend(assertions_config)
        if case.assert_rules:
            try:
                combined_assertions.extend(json.loads(case.assert_rules))
            except Exception:
                logger.warning("Replay case %s has invalid assert_rules JSON", case.id)

        assertion_results = evaluate_assertions(
            assertions=combined_assertions,
            replayed_body=mapped_actual_body,
            status_code=actual_status,
            diff_score=diff_score,
        )
        assertion_results_json = json.dumps(assertion_results, ensure_ascii=False)

        status_ok = case.expected_status is None or actual_status == case.expected_status
        diff_ok = diff_json is None
        assertions_ok = assertions_all_passed(assertion_results)
        perf_ok = perf_threshold_ms is None or latency_ms <= perf_threshold_ms

        if status_ok and diff_ok and assertions_ok and perf_ok:
            status = "PASS"
            is_pass = True
        else:
            status = "FAIL"
            failure_category = (
                "status_mismatch"
                if not status_ok
                else ("response_diff" if not diff_ok else ("assertion_failed" if not assertions_ok else "performance"))
            )
            failure_reason = _build_failure_reason(
                status_ok=status_ok,
                expected_status=case.expected_status,
                actual_status=actual_status,
                diff_ok=diff_ok,
                diff_json=diff_json,
                assertions_ok=assertions_ok,
                assertion_results=assertion_results,
                perf_ok=perf_ok,
                latency_ms=latency_ms,
                perf_threshold_ms=perf_threshold_ms,
            )

    actual_sub_calls_json = None
    if status in ("OK_GOT_RESPONSE", "PASS", "FAIL"):
        if replay_arex_record_id:
            actual_sub_calls_json = await _fetch_replay_sub_calls(
                replay_arex_record_id,
                case=case,
                anchor_created_at_ms=replay_completed_at_ms,
            )
        elif case and case.request_body:
            logger.warning(
                "Replay case %s response missing arex-record-id; attempting reconstructed sub-call fallback",
                case.id,
            )
            actual_sub_calls_json = await _fetch_replay_sub_calls(
                None,
                case=case,
                anchor_created_at_ms=replay_completed_at_ms,
            )
        await _append_replay_audit_log(
            job_id=job_id,
            test_case_id=case_id,
            application_id=application_id,
            event_type="sub_calls_captured",
            request_method=case.request_method,
            request_uri=case.request_uri,
            transaction_code=transaction_code,
            message="已抓取回放子调用",
            detail={
                "replay_arex_record_id": replay_arex_record_id,
                "sub_call_count": len(json.loads(actual_sub_calls_json)) if actual_sub_calls_json else 0,
            },
        )

    # Retrieve expected sub-calls (from source recording) for diff detail computation.
    # This is intentionally independent from actual_sub_calls_json so strict mode
    # can fail when the replay agent reports no sub-calls at all.
    expected_sub_calls_json = None
    recording_found = False
    if case and case.source_recording_id:
        async with database.async_session_factory() as _sc_db:
            _rec = (await _sc_db.execute(
                select(Recording).where(Recording.id == case.source_recording_id)
            )).scalar_one_or_none()
            if _rec:
                expected_sub_calls_json = _rec.sub_calls
                recording_found = True
    # Build per-pair sub-call diff detail (always, for display in UI)
    sub_call_diff_detail_json = None
    if recording_found:
        _sc_pairs = _build_sub_call_diff_pairs(
            expected_sub_calls_json,
            actual_sub_calls_json,
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields or None,
            diff_rules=diff_rules if diff_rules else None,
            ignore_order=ignore_order,
        )
        if _sc_pairs:
            sub_call_diff_detail_json = json.dumps(_sc_pairs, ensure_ascii=False)

    if fail_on_sub_call_diff and is_pass and recording_found:
        # Only compare sub-calls when the test case originates from a recording.
        # If there is no source_recording_id (manually created case) or the
        # recording cannot be found, skip the check entirely – we have no
        # baseline to compare against and must not mark the result as FAIL.
        sub_call_failure = _strict_sub_call_failure(
            expected_sub_calls_json=expected_sub_calls_json,
            actual_sub_calls_json=actual_sub_calls_json,
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields or None,
            diff_rules=diff_rules if diff_rules else None,
            ignore_order=ignore_order,
        )
        if sub_call_failure:
            is_pass = False
            status = "FAIL"
            failure_category, failure_reason = sub_call_failure

    result = await _save_result(
        job_id=job_id,
        case_id=case_id,
        case=case,
        status=status,
        actual_status_code=actual_status,
        actual_response=mapped_actual_body,
        expected_response=case.expected_response,
        diff_result=diff_json,
        diff_score=diff_score,
        assertion_results=assertion_results_json,
        is_pass=is_pass,
        latency_ms=latency_ms,
        failure_category=failure_category,
        failure_reason=failure_reason,
        actual_sub_calls=actual_sub_calls_json,
        sub_call_diff_detail=sub_call_diff_detail_json,
    )
    await _append_replay_audit_log(
        job_id=job_id,
        result_id=getattr(result, "id", None),
        test_case_id=case_id,
        application_id=application_id,
        level="INFO" if status in ("PASS", "FAIL") else "ERROR",
        event_type="case_finished",
        target_url=url,
        request_method=case.request_method,
        request_uri=case.request_uri,
        transaction_code=transaction_code,
        actual_status_code=actual_status,
        latency_ms=latency_ms,
        message="回放用例执行结束",
        detail={
            "status": status,
            "is_pass": is_pass,
            "failure_category": failure_category,
            "failure_reason": failure_reason,
            "diff_score": diff_score,
        },
    )
    return result
