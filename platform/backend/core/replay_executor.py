"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import json
import logging
import re
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

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
from utils.governance import infer_transaction_code
from utils.repository_capture import is_noise_dynamic_mocker, normalize_repository_sub_call
from utils.timezone import now_beijing
from utils.transaction_mapping import apply_transaction_mapping, normalize_transaction_mapping_configs

logger = logging.getLogger(__name__)
# Empirical wait for AREX agent to finish async reporting after replay.
# Configurable via AR_AREX_FLUSH_DELAY_S in .env (default 1.0s).
# Known limitation: under high load, agent may take longer than this to flush,
# causing sub-calls to be silently missed (frontend shows "Agent 未上报").
_AREX_AGENT_FLUSH_DELAY_S: float = settings.arex_flush_delay_s
_SIBLING_SERVLET_LOOKAROUND_MS = 5000

_ws_connections: dict[int, set] = {}


def _sub_calls_have_diff(expected_json: str | None, actual_json: str | None) -> bool:
    """Return True if recorded vs replayed sub-calls have meaningful differences.

    Differences are: count mismatch, unmatched call (recorded-only / replayed-only),
    or response content change on a matched pair.
    """
    try:
        expected: list = json.loads(expected_json) if expected_json else []
        actual: list = json.loads(actual_json) if actual_json else []
    except Exception:
        return False

    if not isinstance(expected, list):
        expected = []
    if not isinstance(actual, list):
        actual = []

    if len(expected) != len(actual):
        return True

    # Try to pair each expected call with the best-matching actual call (greedy)
    unmatched = set(range(len(actual)))
    for exp_item in expected:
        if not isinstance(exp_item, dict):
            continue
        exp_type = str(exp_item.get("type") or "").lower()
        exp_op = str(exp_item.get("operation") or "").lower()

        best_idx = None
        for i in unmatched:
            act_item = actual[i]
            if not isinstance(act_item, dict):
                continue
            act_type = str(act_item.get("type") or "").lower()
            act_op = str(act_item.get("operation") or "").lower()
            if exp_type == act_type and exp_op == act_op:
                best_idx = i
                break

        if best_idx is None:
            return True  # recorded call has no match in actual

        unmatched.remove(best_idx)
        act_item = actual[best_idx]

        # Compare responses (deep equality)
        if _deep_equal(exp_item.get("response"), act_item.get("response")) is False:
            return True

    if unmatched:
        return True  # extra calls only in actual

    return False


def _deep_equal(left, right) -> bool:
    """Recursive equality check for sub-call response values."""
    if isinstance(left, str):
        try:
            left = json.loads(left)
        except Exception:
            pass
    if isinstance(right, str):
        try:
            right = json.loads(right)
        except Exception:
            pass

    if isinstance(left, dict) and isinstance(right, dict):
        if set(left.keys()) != set(right.keys()):
            return False
        return all(_deep_equal(left[k], right[k]) for k in left)

    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False
        return all(_deep_equal(a, b) for a, b in zip(left, right))

    return left == right


def _extract_xml_tag_text(text: str | None, *tag_names: str) -> str | None:
    if not text:
        return None
    for tag_name in tag_names:
        match = re.search(rf"<{tag_name}>([^<]+)</{tag_name}>", text)
        if match:
            return match.group(1).strip()
    return None


def _parse_json_like(value):
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except Exception:
            return text
    return value


def _normalize_http_headers(value) -> dict[str, list[str]]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            value = None
    if not isinstance(value, dict):
        return {}

    normalized: dict[str, list[str]] = {}
    for key, item in value.items():
        if item is None:
            continue
        if isinstance(item, list):
            normalized[str(key)] = [str(entry) for entry in item if entry is not None]
        else:
            normalized[str(key)] = [str(item)]
    return normalized


def _build_http_sub_call_from_sibling_servlet(mocker: dict) -> dict | None:
    target_request = mocker.get("targetRequest") or {}
    request_attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    endpoint = (
        request_attrs.get("RequestPath")
        or request_attrs.get("requestPath")
        or mocker.get("operationName")
        or ""
    )
    if not endpoint:
        return None

    parsed_endpoint = urlparse(endpoint)
    operation = parsed_endpoint.path or endpoint
    method = request_attrs.get("HttpMethod") or request_attrs.get("httpMethod") or "GET"
    target_response = mocker.get("targetResponse") or {}
    response_attrs = (target_response.get("attributes") or {}) if isinstance(target_response, dict) else {}
    response_headers = _normalize_http_headers(
        response_attrs.get("Headers") or response_attrs.get("headers")
    )

    status_code = (
        response_attrs.get("StatusCode")
        or response_attrs.get("statusCode")
        or response_attrs.get("HttpStatus")
        or response_attrs.get("httpStatus")
    )
    if status_code is not None:
        try:
            status_code = int(status_code)
        except (TypeError, ValueError):
            status_code = None
    response_body = _parse_json_like(target_response.get("body") if isinstance(target_response, dict) else target_response)
    if status_code is None and response_body is not None:
        # Detached internal Servlet rows observed in replay fallback often omit
        # explicit HTTP status metadata even when the invocation succeeded.
        status_code = 200

    response_payload = None
    if status_code is not None or response_body is not None or response_headers:
        response_payload = {}
        if status_code is not None:
            response_payload["httpStatus"] = status_code
        if response_body is not None:
            response_payload["body"] = response_body
        if response_headers:
            response_payload["headers"] = response_headers

    request_body = target_request.get("body") if isinstance(target_request, dict) else target_request
    request_value = request_body
    if request_value in (None, ""):
        request_value = json.dumps({"responseType": "java.util.Map"}, ensure_ascii=False, separators=(",", ":"))
    elif not isinstance(request_value, str):
        request_value = json.dumps(request_value, ensure_ascii=False)

    return {
        "type": "HttpClient",
        "source": "sibling_servlet",
        "operation": operation,
        "request": request_value,
        "response": response_payload,
        "method": str(method).upper(),
        "endpoint": endpoint,
    }


async def _fetch_replay_sibling_internal_http_sub_calls(
    db,
    *,
    app_identifier: str | None,
    case: Optional[TestCase],
    anchor_created_at_ms: Optional[int],
) -> list[dict]:
    if not app_identifier or not case or not case.request_body or anchor_created_at_ms is None:
        return []

    from api.v1.sessions import _DIDI_COMPLEX_TRANSACTION_CODES

    txn_code = infer_transaction_code(case.request_body)
    if txn_code not in _DIDI_COMPLEX_TRANSACTION_CODES:
        return []

    tra_id = _extract_xml_tag_text(case.request_body, "tra_id", "traId")
    if not txn_code and not tra_id:
        return []

    result = await db.execute(
        select(ArexMocker)
        .where(
            ArexMocker.app_id == app_identifier,
            ArexMocker.category_name == "Servlet",
            ArexMocker.is_entry_point == True,  # noqa: E712
            ArexMocker.created_at_ms >= max(anchor_created_at_ms - _SIBLING_SERVLET_LOOKAROUND_MS, 0),
            ArexMocker.created_at_ms <= anchor_created_at_ms + _SIBLING_SERVLET_LOOKAROUND_MS,
        )
        .order_by(ArexMocker.created_at_ms, ArexMocker.id)
    )
    rows = result.scalars().all()

    sibling_sub_calls: list[dict] = []
    for row in rows:
        try:
            mocker = json.loads(row.mocker_data)
            target_request = mocker.get("targetRequest") or {}
            request_attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
            endpoint = (
                request_attrs.get("RequestPath")
                or request_attrs.get("requestPath")
                or mocker.get("operationName")
                or ""
            )
            if not endpoint.startswith("/internal/didi/"):
                continue

            parsed_endpoint = urlparse(endpoint)
            query_params = {
                key: values[-1]
                for key, values in parse_qs(parsed_endpoint.query, keep_blank_values=True).items()
                if values
            }
            row_txn_code = query_params.get("txnCode") or query_params.get("txn_code")
            row_tra_id = query_params.get("traId") or query_params.get("tra_id")
            if txn_code and row_txn_code != txn_code:
                continue
            if tra_id and row_tra_id != tra_id:
                continue

            sub_call = _build_http_sub_call_from_sibling_servlet(mocker)
            if sub_call is not None:
                sibling_sub_calls.append(sub_call)
        except Exception as exc:
            logger.warning("Failed to parse sibling Servlet ArexMocker %s: %s", row.id, exc)

    return sibling_sub_calls


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

        job.status = "RUNNING"
        job.total = len(case_ids)
        job.started_at = now_beijing()
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
    job_fail_on_sub_call_diff = job.fail_on_sub_call_diff

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
                fail_on_sub_call_diff=job_fail_on_sub_call_diff,
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
                    fail_on_sub_call_diff=job_fail_on_sub_call_diff,
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
        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            job.status = "FAILED" if failed > 0 or errored > 0 else "DONE"
            job.passed = passed
            job.failed = failed
            job.errored = errored
            job.finished_at = now_beijing()
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
    fail_on_sub_call_diff: bool = False,
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
    replay_completed_at_ms = None

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
        replay_arex_record_id = resp.headers.get("arex-record-id")
        replay_completed_at_ms = int(time.time() * 1000)
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

    if fail_on_sub_call_diff and is_pass and actual_sub_calls_json:
        # Only compare sub-calls when the test case originates from a recording.
        # If there is no source_recording_id (manually created case) or the
        # recording cannot be found, skip the check entirely – we have no
        # baseline to compare against and must not mark the result as FAIL.
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
        if recording_found and _sub_calls_have_diff(expected_sub_calls_json, actual_sub_calls_json):
            is_pass = False
            status = "FAIL"
            failure_category = "sub_call_diff"
            failure_reason = "子调用差异"

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


async def _fetch_replay_sub_calls(
    record_id: Optional[str],
    case: Optional[TestCase] = None,
    anchor_created_at_ms: Optional[int] = None,
) -> Optional[str]:
    """Fetch replay sub-calls from AREX or fall back to app-specific reconstruction.

    When `record_id` is present, this waits for AREX agent flush and loads reported
    sub-calls for that replay record. When it is absent, only best-effort app-aware
    reconstruction (for example Didi DB sub-calls) is attempted.
    """
    if record_id:
        await asyncio.sleep(_AREX_AGENT_FLUSH_DELAY_S)
    async with database.async_session_factory() as db:
        mockers = []
        if record_id:
            result = await db.execute(
                select(ArexMocker)
                .where(
                    ArexMocker.record_id == record_id,
                    ArexMocker.is_entry_point == False,  # noqa: E712
                )
                .order_by(ArexMocker.id)
            )
            mockers = result.scalars().all()
        app_identifier = None
        if case and case.application_id:
            app_result = await db.execute(
                select(Application).where(Application.id == case.application_id)
            )
            app = app_result.scalar_one_or_none()
            if app:
                app_identifier = app.arex_app_id or app.name

        sub_calls = []
        for m in mockers:
            try:
                mocker = json.loads(m.mocker_data)
                category = mocker.get("categoryType") or {}
                cat_name = category.get("name") if isinstance(category, dict) else str(category)
                operation_name = mocker.get("operationName") or ""
                if is_noise_dynamic_mocker(operation_name, cat_name or m.category_name):
                    continue
                repository_sub_call = normalize_repository_sub_call(mocker, cat_name or m.category_name)
                if repository_sub_call is not None:
                    sub_calls.append(repository_sub_call)
                    continue
                target_req = mocker.get("targetRequest") or {}
                target_resp = mocker.get("targetResponse") or {}
                sub_calls.append({
                    "type": cat_name or m.category_name,
                    "operation": operation_name,
                    "request": target_req.get("body") if isinstance(target_req, dict) else None,
                    "response": target_resp.get("body") if isinstance(target_resp, dict) else None,
                })
            except Exception as exc:
                logger.warning("Failed to parse ArexMocker %s: %s", m.id, exc)

        try:
            from api.v1.sessions import (
                _exclude_duplicate_database_sub_calls,
                _fetch_didi_sub_calls,
                _merge_sub_calls,
            )

            sibling_http_sub_calls = await _fetch_replay_sibling_internal_http_sub_calls(
                db,
                app_identifier=app_identifier or next((m.app_id for m in mockers if m.app_id), ""),
                case=case,
                anchor_created_at_ms=anchor_created_at_ms,
            )
            if sibling_http_sub_calls:
                existing_http_operations = {
                    str(item.get("operation") or "")
                    for item in sub_calls
                    if isinstance(item, dict) and str(item.get("type") or "").lower() == "httpclient"
                }
                missing_http_sub_calls = [
                    item
                    for item in sibling_http_sub_calls
                    if str(item.get("operation") or "") not in existing_http_operations
                ]
                if missing_http_sub_calls:
                    sub_calls = _merge_sub_calls(sub_calls, missing_http_sub_calls)

            didi_sub_calls = await _fetch_didi_sub_calls(
                case.request_body,
                app_identifier or next((m.app_id for m in mockers if m.app_id), ""),
            )
            if didi_sub_calls:
                sub_calls = _exclude_duplicate_database_sub_calls(didi_sub_calls, sub_calls)
                sub_calls = _merge_sub_calls(sub_calls, didi_sub_calls)
        except Exception as exc:
            logger.warning("Failed to enrich replay sub-calls for %s: %s", record_id or "<missing>", exc)

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
