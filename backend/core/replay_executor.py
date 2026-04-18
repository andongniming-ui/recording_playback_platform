"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import json
import logging
import time
from typing import Optional

import httpx
from sqlalchemy import or_, select

from config import settings
import database
from integration.arex_client import ArexClient, ArexClientError
from models.application import Application
from models.compare import CompareRule
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.arex_mocker import ArexMocker
from models.test_case import TestCase
from utils.assertions import assertions_all_passed, evaluate_assertions
from utils.diff import compute_diff
from utils.transaction_mapping import apply_transaction_mapping, normalize_transaction_mapping_configs

logger = logging.getLogger(__name__)

_ws_connections: dict[int, set] = {}


def register_ws(job_id: int, ws):
    _ws_connections.setdefault(job_id, set()).add(ws)


def unregister_ws(job_id: int, ws):
    if job_id in _ws_connections:
        _ws_connections[job_id].discard(ws)


def _load_json_value(raw: str | None, label: str, default):
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        logger.warning("Invalid JSON for %s", label)
        return default


def _normalize_rule_entries(value) -> list[dict]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def _collect_compare_rule_effects(rule: CompareRule) -> tuple[list[str], list[dict], list[dict]]:
    config = _load_json_value(rule.config, f"compare rule {rule.id}", default=None)
    entries = _normalize_rule_entries(config)
    ignore_fields: list[str] = []
    diff_rule_entries: list[dict] = []
    assertion_entries: list[dict] = []

    for entry in entries:
        if rule.rule_type == "ignore":
            if entry.get("path"):
                normalized = dict(entry)
                normalized["type"] = normalized.get("type") or "ignore"
                diff_rule_entries.append(normalized)
            elif entry.get("key"):
                ignore_fields.append(str(entry["key"]))
            elif entry.get("field"):
                ignore_fields.append(str(entry["field"]))
        elif rule.rule_type == "assert" and entry.get("type"):
            assertion_entries.append(entry)

    return ignore_fields, diff_rule_entries, assertion_entries


def _apply_header_transforms(headers: dict, transforms) -> dict:
    if not isinstance(headers, dict):
        headers = {}
    result = {
        str(key): "" if value is None else str(value)
        for key, value in headers.items()
    }
    entries = _normalize_rule_entries(transforms)
    for entry in entries:
        transform_type = str(entry.get("type") or "replace").lower()
        key = str(entry.get("key") or "").strip()
        if not key:
            continue
        if transform_type == "remove":
            matched = next((existing for existing in result if existing.lower() == key.lower()), None)
            if matched:
                result.pop(matched, None)
            continue
        value = "" if entry.get("value") is None else str(entry.get("value"))
        matched = next((existing for existing in result if existing.lower() == key.lower()), None)
        result[matched or key] = value
    return result


def _extract_diff_paths(diff_json: str | None, limit: int = 5) -> list[str]:
    if not diff_json:
        return []
    try:
        payload = json.loads(diff_json)
    except Exception:
        return []
    paths: list[str] = []
    for change_type, items in payload.items():
        if not isinstance(items, dict):
            continue
        for raw_path in items.keys():
            normalized = (
                str(raw_path)
                .replace("root", "")
                .replace("']['", ".")
                .replace("['", ".")
                .replace("']", "")
                .replace("[", ".")
                .replace("]", "")
                .lstrip(".")
            )
            if normalized and normalized not in paths:
                paths.append(normalized)
            if len(paths) >= limit:
                return paths
    return paths


def _build_failure_reason(
    *,
    status_ok: bool,
    expected_status: Optional[int],
    actual_status: Optional[int],
    diff_ok: bool,
    diff_json: str | None,
    assertions_ok: bool,
    assertion_results: list[dict],
    perf_ok: bool,
    latency_ms: Optional[int],
    perf_threshold_ms: Optional[int],
) -> str:
    if not status_ok:
        return f"状态码不一致：期望 {expected_status}，实际 {actual_status}"
    if not diff_ok:
        diff_paths = _extract_diff_paths(diff_json)
        if diff_paths:
            return f"响应内容不一致：差异字段 {', '.join(diff_paths)}"
        return "响应内容不一致"
    if not assertions_ok:
        failed_messages = [
            str(item.get("message"))
            for item in assertion_results
            if isinstance(item, dict) and not item.get("passed", False) and item.get("message")
        ]
        if failed_messages:
            return f"断言失败：{failed_messages[0]}"
        return "断言失败"
    return f"耗时超阈值：{latency_ms}ms > {perf_threshold_ms}ms"


def _normalize_mappings(raw) -> list[dict]:
    return normalize_transaction_mapping_configs(raw)


async def _broadcast_progress(job_id: int, data: dict):
    conns = _ws_connections.get(job_id, set())
    dead = set()
    for ws in conns:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    for ws in dead:
        conns.discard(ws)


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

        compare_rule_stmt = select(CompareRule).where(CompareRule.is_active == True)
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

        from datetime import datetime, timezone

        job.status = "RUNNING"
        job.total = len(case_ids)
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

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

    # 流量放大：将每条 case 重复回放 repeat_count 次
    job_repeat_count = max(1, job.repeat_count or 1)
    if job_repeat_count > 1:
        case_ids = case_ids * job_repeat_count
        # 更新 total 为实际执行数
        async with database.async_session_factory() as _db:
            _result = await _db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            _job = _result.scalar_one_or_none()
            if _job:
                _job.total = len(case_ids)
                await _db.commit()

    # 从 job 读取 target_host 覆盖
    if job.target_host:
        target_host = job.target_host

    semaphore = asyncio.Semaphore(job.concurrency)
    progress_lock = asyncio.Lock()
    done_count = 0
    passed = 0
    failed = 0
    errored = 0
    job_smart_noise_reduction = job.smart_noise_reduction
    job_retry_count = job.retry_count

    async def _run_one(case_id: int):
        nonlocal done_count, passed, failed, errored
        case = case_map.get(case_id)
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
                header_transforms=header_transforms,
                transaction_mappings=transaction_mappings,
            )
            # P1: 失败重试
            for _attempt in range(job_retry_count):
                if result.status not in ("FAIL", "ERROR", "TIMEOUT"):
                    break
                logger.info(
                    "Replay case %s failed (status=%s), retrying (%d/%d)…",
                    case_id, result.status, _attempt + 1, job_retry_count,
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
                    header_transforms=header_transforms,
                    transaction_mappings=transaction_mappings,
                )

        async with progress_lock:
            done_count += 1
            if result.status == "PASS":
                passed += 1
            elif result.status in ("FAIL", "TIMEOUT"):
                failed += 1
            else:
                errored += 1

            async with database.async_session_factory() as progress_db:
                job_result = await progress_db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
                progress_job = job_result.scalar_one_or_none()
                if progress_job:
                    progress_job.passed = passed
                    progress_job.failed = failed
                    progress_job.errored = errored
                    await progress_db.commit()

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

    await asyncio.gather(*[_run_one(case_id) for case_id in case_ids])

    async with database.async_session_factory() as db:
        from datetime import datetime, timezone

        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            job.status = "FAILED" if failed > 0 or errored > 0 else "DONE"
            job.passed = passed
            job.failed = failed
            job.errored = errored
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()

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
    header_transforms=None,
    transaction_mappings: list[dict] | None = None,
) -> ReplayResult:
    """Execute one test case and save the result back into the placeholder row."""
    if not case:
        return await _save_result(
            job_id=job_id,
            case_id=case_id,
            status="ERROR",
            is_pass=False,
            failure_category="connection_error",
            failure_reason="Test case not found",
        )

    mock_record_id = None
    replay_arex_record_id = None
    if use_mocks:
        if not case.source_recording_id:
            return await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="use_sub_invocation_mocks requires a test case created from a recording",
            )
        async with database.async_session_factory() as db:
            recording_result = await db.execute(
                select(Recording).where(Recording.id == case.source_recording_id)
            )
            recording = recording_result.scalar_one_or_none()
        if not recording or not recording.record_id:
            return await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="Source recording not found or missing AREX record_id",
            )
        mock_record_id = recording.record_id

    base_url = target_host or "http://localhost:8080"
    url = f"{base_url}{case.request_uri}"
    transaction_code = getattr(case, "transaction_code", None)

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
    mock_client = ArexClient(arex_storage_url)
    mock_loaded = False

    try:
        if use_mocks and mock_record_id:
            await mock_client.cache_load_mock(mock_record_id)
            mock_loaded = True

        timeout = httpx.Timeout(timeout_ms / 1000.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=case.request_method or "GET",
                url=url,
                content=mapped_request_body.encode() if mapped_request_body else None,
                headers=headers,
            )
        actual_status = resp.status_code
        actual_body = resp.text
        replay_arex_record_id = getattr(resp, "headers", {}).get("arex-record-id")
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "OK_GOT_RESPONSE"
    except httpx.TimeoutException:
        latency_ms = timeout_ms
        status = "TIMEOUT"
        failure_category = "timeout"
        failure_reason = f"Request timed out after {timeout_ms}ms"
    except ArexClientError as exc:
        latency_ms = 0
        status = "ERROR"
        failure_category = "mock_error"
        failure_reason = str(exc)
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "ERROR"
        failure_category = "connection_error"
        failure_reason = str(exc)
    finally:
        if mock_loaded and mock_record_id:
            try:
                await mock_client.cache_remove_mock(mock_record_id)
            except Exception as exc:
                logger.warning("Failed to remove AREX mock cache for %s: %s", mock_record_id, exc)

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
        ignore_fields = list(base_ignore_fields or [])
        if case.ignore_fields:
            try:
                case_ignore_fields = json.loads(case.ignore_fields)
                if isinstance(case_ignore_fields, list):
                    ignore_fields.extend(case_ignore_fields)
            except Exception:
                logger.warning("Replay case %s has invalid ignore_fields JSON", case.id)

        diff_json, diff_score = compute_diff(
            original=case.expected_response,
            replayed=mapped_actual_body,
            diff_rules=diff_rules,
            ignore_fields=ignore_fields,
            smart_noise_reduction=smart_noise_reduction,
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
    if replay_arex_record_id and status not in ("TIMEOUT", "ERROR"):
        actual_sub_calls_json = await _fetch_replay_sub_calls(replay_arex_record_id)

    return await _save_result(
        job_id=job_id,
        case_id=case_id,
        case=case,
        status=status,
        actual_status_code=actual_status,
        actual_response=mapped_actual_body if status == "OK_GOT_RESPONSE" else actual_body,
        expected_response=case.expected_response,
        diff_result=diff_json,
        diff_score=diff_score,
        assertion_results=assertion_results_json,
        is_pass=is_pass,
        latency_ms=latency_ms,
        failure_category=failure_category,
        failure_reason=failure_reason,
        actual_sub_calls=actual_sub_calls_json,
    )


async def _fetch_replay_sub_calls(record_id: str) -> Optional[str]:
    """Wait for AREX agent to finish reporting, then fetch sub-calls by record_id."""
    await asyncio.sleep(0.3)
    async with database.async_session_factory() as db:
        result = await db.execute(
            select(ArexMocker)
            .where(
                ArexMocker.record_id == record_id,
                ArexMocker.is_entry_point == False,  # noqa: E712
            )
            .order_by(ArexMocker.id)
        )
        mockers = result.scalars().all()
    if not mockers:
        return None
    sub_calls = []
    for m in mockers:
        try:
            mocker = json.loads(m.mocker_data)
            category = mocker.get("categoryType") or {}
            cat_name = category.get("name") if isinstance(category, dict) else str(category)
            target_req = mocker.get("targetRequest") or {}
            target_resp = mocker.get("targetResponse") or {}
            sub_calls.append({
                "type": cat_name or m.category_name,
                "operation": mocker.get("operationName") or "",
                "request": target_req.get("body") if isinstance(target_req, dict) else None,
                "response": target_resp.get("body") if isinstance(target_resp, dict) else None,
            })
        except Exception:
            pass
    return json.dumps(sub_calls, ensure_ascii=False) if sub_calls else None


async def _save_result(
    job_id: int,
    case_id: int,
    *,
    case: Optional[TestCase] = None,
    status: str,
    is_pass: bool,
    actual_status_code: Optional[int] = None,
    actual_response: Optional[str] = None,
    expected_response: Optional[str] = None,
    diff_result: Optional[str] = None,
    diff_score: Optional[float] = None,
    assertion_results: Optional[str] = None,
    latency_ms: Optional[int] = None,
    failure_category: Optional[str] = None,
    failure_reason: Optional[str] = None,
    actual_sub_calls: Optional[str] = None,
) -> ReplayResult:
    """Update the placeholder replay result for a case, or create one if missing."""
    async with database.async_session_factory() as db:
        result = await db.execute(
            select(ReplayResult)
            .where(ReplayResult.job_id == job_id, ReplayResult.test_case_id == case_id)
            .order_by(ReplayResult.id)
        )
        replay_result = result.scalars().first()

        if replay_result is None:
            replay_result = ReplayResult(
                job_id=job_id,
                test_case_id=case_id,
                status="PENDING",
                is_pass=False,
            )
            db.add(replay_result)

        replay_result.status = status
        replay_result.request_method = case.request_method if case else None
        replay_result.request_uri = case.request_uri if case else None
        replay_result.actual_status_code = actual_status_code
        replay_result.actual_response = actual_response
        replay_result.expected_response = expected_response
        replay_result.diff_result = diff_result
        replay_result.diff_score = diff_score
        replay_result.assertion_results = assertion_results
        replay_result.is_pass = is_pass
        replay_result.latency_ms = latency_ms
        replay_result.failure_category = failure_category
        replay_result.failure_reason = failure_reason
        replay_result.actual_sub_calls = actual_sub_calls

        await db.commit()
        await db.refresh(replay_result)
        return replay_result
