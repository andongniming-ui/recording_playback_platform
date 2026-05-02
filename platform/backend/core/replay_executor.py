"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import base64
import json
import logging
import re
import time
from typing import Optional
from urllib.parse import parse_qs, urlparse

import httpx
from sqlalchemy import func, or_, select, update

from config import settings
import database
from integration.arex_client import ArexClient, ArexClientError
from models.application import Application
from models.audit import ReplayAuditLog
from models.compare import CompareRule
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.arex_mocker import ArexMocker
from models.test_case import TestCase
from utils.assertions import assertions_all_passed, evaluate_assertions
from utils.diff import compute_diff
from utils.governance import infer_transaction_code
from utils.repository_capture import (
    is_noise_dynamic_mocker,
    normalize_generic_database_sub_call,
    normalize_repository_sub_call,
)
from utils.timezone import now_beijing
from utils.transaction_mapping import apply_transaction_mapping, normalize_transaction_mapping_configs
from utils.serialization import json_text
from utils.sub_call_matcher import (
    normalize_sub_call_type,
    normalize_http_operation,
    normalize_sub_call_operation,
    normalize_sub_call_value,
    parse_sub_call_payload,
    unwrap_sub_call_response,
)

logger = logging.getLogger(__name__)
# Empirical wait for AREX agent to finish async reporting after replay.
# Configurable via AR_AREX_FLUSH_DELAY_S in .env (default 1.0s).
# Known limitation: under high load, agent may take longer than this to flush,
# causing sub-calls to be silently missed (frontend shows "Agent 未上报").
_AREX_AGENT_FLUSH_DELAY_S: float = settings.arex_flush_delay_s
_SIBLING_SERVLET_LOOKAROUND_MS = 5000
_REPLAY_ENTRY_LOOKAROUND_MS = 10000

_ws_connections: dict[int, set] = {}
_ws_connections_lock = asyncio.Lock()


def _decode_possible_base64_text(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    try:
        decoded = base64.b64decode(value, validate=True).decode("utf-8")
        if decoded.strip():
            return decoded
    except Exception:
        pass
    return value


def _collect_scalar_tokens(value, tokens: set[str]) -> None:
    if value is None:
        return
    if isinstance(value, dict):
        for item in value.values():
            _collect_scalar_tokens(item, tokens)
        return
    if isinstance(value, list):
        for item in value:
            _collect_scalar_tokens(item, tokens)
        return
    text = str(value).strip()
    if len(text) >= 6:
        tokens.add(text)


def _case_correlation_tokens(case: Optional[TestCase]) -> set[str]:
    if not case:
        return set()

    tokens: set[str] = set()
    parsed = urlparse(case.request_uri or "")
    for values in parse_qs(parsed.query, keep_blank_values=False).values():
        for value in values:
            if len(str(value).strip()) >= 6:
                tokens.add(str(value).strip())

    body = case.request_body
    if body:
        try:
            _collect_scalar_tokens(json.loads(body), tokens)
        except Exception:
            # Handles simple XML/form bodies without adding short field names.
            for match in re.findall(r">([^<>]{6,})<", body):
                tokens.add(match.strip())
            for match in re.findall(r"[:=]\s*['\"]?([A-Za-z0-9_\-]{6,})", body):
                tokens.add(match.strip())

    return tokens


def _sibling_mocker_correlation_text(mocker: dict) -> str:
    target_request = mocker.get("targetRequest") or {}
    request_attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    endpoint = (
        request_attrs.get("RequestPath")
        or request_attrs.get("requestPath")
        or mocker.get("operationName")
        or ""
    )
    body = target_request.get("body") if isinstance(target_request, dict) else target_request
    return f"{endpoint}\n{_decode_possible_base64_text(body)}"


async def _append_replay_audit_log(
    *,
    job_id: int,
    result_id: int | None = None,
    test_case_id: int | None = None,
    application_id: int | None = None,
    level: str = "INFO",
    event_type: str,
    target_url: str | None = None,
    request_method: str | None = None,
    request_uri: str | None = None,
    transaction_code: str | None = None,
    actual_status_code: int | None = None,
    latency_ms: int | None = None,
    message: str | None = None,
    detail=None,
) -> None:
    try:
        async with database.async_session_factory() as db:
            if not hasattr(db, "add"):
                return
            db.add(
                ReplayAuditLog(
                    job_id=job_id,
                    result_id=result_id,
                    test_case_id=test_case_id,
                    application_id=application_id,
                    level=level,
                    event_type=event_type,
                    target_url=target_url,
                    request_method=request_method,
                    request_uri=request_uri,
                    transaction_code=transaction_code,
                    actual_status_code=actual_status_code,
                    latency_ms=latency_ms,
                    message=message,
                    detail=json_text(detail),
                )
            )
            await db.commit()
    except Exception as exc:
        logger.warning("Failed to persist replay audit log job=%s event=%s: %s", job_id, event_type, exc)


def _sub_calls_have_diff(
    expected_json: str | None,
    actual_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> bool:
    """Return True if recorded vs replayed sub-calls have meaningful differences.

    Differences are: count mismatch, unmatched call (recorded-only / replayed-only),
    or response content change on a matched pair.

    Args:
        smart_noise_reduction: When True, apply built-in noise patterns (30+ dynamic
            fields like timestamps, IDs, tokens) before comparing responses.
        ignore_fields: Additional field names to exclude from response comparison.
        diff_rules: Smart diff rules (same format as main response comparison).
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

    unmatched = list(range(len(actual)))
    for exp_item in expected:
        if not isinstance(exp_item, dict):
            continue

        best_idx = None
        best_score = None
        for i in unmatched:
            act_item = actual[i]
            score = _sub_call_match_score(exp_item, act_item)
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_idx = i
                best_score = score

        if best_idx is None:
            return True  # recorded call has no match in actual

        unmatched.remove(best_idx)
        act_item = actual[best_idx]

        if _sub_call_responses_have_diff(
            exp_item.get("response"),
            act_item.get("response"),
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        ):
            return True

    if unmatched:
        return True  # extra calls only in actual

    return False




def _sub_call_request_signature(item: dict | None) -> str:
    if not isinstance(item, dict):
        return ""
    parts = []
    for key in ("sql", "sql_text", "params", "request", "method", "endpoint"):
        normalized = normalize_sub_call_value(item.get(key))
        if normalized:
            parts.append(f"{key}={normalized}")
    return "\n".join(parts)


def _sub_call_match_score(expected_item: dict | None, actual_item: dict | None) -> int | None:
    if not isinstance(expected_item, dict) or not isinstance(actual_item, dict):
        return None

    expected_type = normalize_sub_call_type(expected_item.get("type"))
    actual_type = normalize_sub_call_type(actual_item.get("type"))
    if expected_type != actual_type:
        return None

    expected_operation = normalize_sub_call_operation(expected_item)
    actual_operation = normalize_sub_call_operation(actual_item)
    if expected_operation and actual_operation and expected_operation != actual_operation:
        return None
    if expected_operation or actual_operation:
        base_score = 2
    else:
        base_score = 0

    expected_signature = _sub_call_request_signature(expected_item)
    actual_signature = _sub_call_request_signature(actual_item)
    if expected_signature and actual_signature:
        if expected_signature == actual_signature:
            return base_score + 3
        return base_score
    return base_score


def _to_diff_text(value) -> str | None:
    if value is None:
        return None
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def _sub_call_responses_have_diff(
    expected_response,
    actual_response,
    *,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> bool:
    expected_response = unwrap_sub_call_response(expected_response)
    actual_response = unwrap_sub_call_response(actual_response)
    if smart_noise_reduction or ignore_fields or diff_rules:
        diff_result, _ = compute_diff(
            original=_to_diff_text(expected_response),
            replayed=_to_diff_text(actual_response),
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        )
        return diff_result is not None
    return not _deep_equal(expected_response, actual_response)


def _sub_call_response_diff_result(
    expected_response,
    actual_response,
    *,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> str | None:
    expected_response = unwrap_sub_call_response(expected_response)
    actual_response = unwrap_sub_call_response(actual_response)
    diff_result, _ = compute_diff(
        original=_to_diff_text(expected_response),
        replayed=_to_diff_text(actual_response),
        smart_noise_reduction=smart_noise_reduction,
        ignore_fields=ignore_fields,
        diff_rules=diff_rules,
        ignore_order=ignore_order,
    )
    return diff_result


def _build_sub_call_diff_pairs(
    expected_json: str | None,
    actual_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> list[dict]:
    """Build per-pair comparison detail between recorded and replayed sub-calls.

    Returns a list of dicts, each representing a comparison pair:
    {
        "type": str,
        "operation": str,
        "matched": bool,          # was a matching actual call found?
        "has_diff": bool,
        "expected_response": ..., # original (None for extra actual-only calls)
        "actual_response": ...,   # replayed (None for missing calls)
        "diff_result": str|None,  # DeepDiff JSON when has_diff else None
    }
    """
    try:
        expected: list = json.loads(expected_json) if expected_json else []
        actual: list = json.loads(actual_json) if actual_json else []
    except Exception:
        return []

    if not isinstance(expected, list):
        expected = []
    if not isinstance(actual, list):
        actual = []

    pairs: list[dict] = []
    unmatched_actual = list(range(len(actual)))

    for exp_item in expected:
        if not isinstance(exp_item, dict):
            continue

        best_idx = None
        best_score = None
        for i in unmatched_actual:
            act_item = actual[i]
            score = _sub_call_match_score(exp_item, act_item)
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_idx = i
                best_score = score

        if best_idx is None:
            pairs.append({
                "type": exp_item.get("type"),
                "operation": exp_item.get("operation"),
                "matched": False,
                "has_diff": True,
                "expected_response": exp_item.get("response"),
                "actual_response": None,
                "diff_result": None,
            })
            continue

        unmatched_actual.remove(best_idx)
        act_item = actual[best_idx]
        exp_resp = exp_item.get("response")
        act_resp = act_item.get("response")

        diff_result_str = _sub_call_response_diff_result(
            exp_resp,
            act_resp,
            smart_noise_reduction=smart_noise_reduction,
            ignore_fields=ignore_fields,
            diff_rules=diff_rules,
            ignore_order=ignore_order,
        )
        has_diff = diff_result_str is not None

        pairs.append({
            "type": exp_item.get("type"),
            "operation": exp_item.get("operation"),
            "matched": True,
            "has_diff": has_diff,
            "expected_response": unwrap_sub_call_response(exp_resp),
            "actual_response": unwrap_sub_call_response(act_resp),
            "diff_result": diff_result_str,
        })

    # Extra calls only in actual (no matching recorded call)
    for i in sorted(unmatched_actual):
        act_item = actual[i]
        if not isinstance(act_item, dict):
            continue
        pairs.append({
            "type": act_item.get("type"),
            "operation": act_item.get("operation"),
            "matched": False,
            "has_diff": True,
            "expected_response": None,
            "actual_response": act_item.get("response"),
            "diff_result": None,
        })

    return pairs


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


def _load_sub_call_list(value: str | None) -> list:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else []


def _count_sub_call_items(value: str | None) -> int:
    return len(_load_sub_call_list(value))


def _strict_sub_call_failure(
    *,
    expected_sub_calls_json: str | None,
    actual_sub_calls_json: str | None,
    smart_noise_reduction: bool = False,
    ignore_fields: list[str] | None = None,
    diff_rules: list[dict] | None = None,
    ignore_order: bool = True,
) -> tuple[str, str] | None:
    expected_count = _count_sub_call_items(expected_sub_calls_json)
    actual_count = _count_sub_call_items(actual_sub_calls_json)
    if expected_count > 0 and actual_count == 0:
        return (
            "sub_call_missing",
            f"回放未抓取到子调用：录制侧 {expected_count} 条，回放侧 0 条",
        )
    if _sub_calls_have_diff(
        expected_sub_calls_json,
        actual_sub_calls_json,
        smart_noise_reduction=smart_noise_reduction,
        ignore_fields=ignore_fields,
        diff_rules=diff_rules,
        ignore_order=ignore_order,
    ):
        return ("sub_call_diff", "子调用差异")
    return None


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


def _entrypoint_mocker_matches_case(mocker: dict, case: Optional[TestCase]) -> bool:
    if not case:
        return False
    target_request = mocker.get("targetRequest") or {}
    request_attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    endpoint = (
        request_attrs.get("RequestPath")
        or request_attrs.get("requestPath")
        or mocker.get("operationName")
        or ""
    )
    if not endpoint:
        return False
    expected_path = urlparse(case.request_uri or "").path or (case.request_uri or "")
    actual_path = urlparse(str(endpoint)).path or str(endpoint).split("?", 1)[0]
    if expected_path and actual_path and expected_path != actual_path:
        return False

    expected_method = (case.request_method or "").upper()
    actual_method = str(request_attrs.get("HttpMethod") or request_attrs.get("httpMethod") or "").upper()
    if expected_method and actual_method and expected_method != actual_method:
        return False

    request_body = target_request.get("body") if isinstance(target_request, dict) else None
    if case.request_body and request_body:
        return str(case.request_body).strip() == str(request_body).strip()
    return True


async def _load_sub_call_mockers(db, record_id: str | None) -> list[ArexMocker]:
    if not record_id:
        return []
    result = await db.execute(
        select(ArexMocker)
        .where(
            ArexMocker.record_id == record_id,
            ArexMocker.is_entry_point.is_(False),
        )
        .order_by(ArexMocker.id)
    )
    return result.scalars().all()


async def _find_recent_entry_record_id(
    db,
    *,
    app_identifier: str | None,
    case: Optional[TestCase],
    anchor_created_at_ms: Optional[int],
) -> str | None:
    if not app_identifier or not case or anchor_created_at_ms is None:
        return None

    result = await db.execute(
        select(ArexMocker)
        .where(
            ArexMocker.app_id == app_identifier,
            ArexMocker.category_name == "Servlet",
            ArexMocker.is_entry_point.is_(True),
            ArexMocker.created_at_ms >= max(anchor_created_at_ms - _REPLAY_ENTRY_LOOKAROUND_MS, 0),
            ArexMocker.created_at_ms <= anchor_created_at_ms + _REPLAY_ENTRY_LOOKAROUND_MS,
        )
        .order_by(ArexMocker.created_at_ms.desc(), ArexMocker.id.desc())
    )
    for row in result.scalars().all():
        try:
            mocker = json.loads(row.mocker_data)
        except Exception:
            continue
        if _entrypoint_mocker_matches_case(mocker, case):
            return row.record_id
    return None


async def _fetch_replay_sibling_internal_http_sub_calls(
    db,
    *,
    app_identifier: str | None,
    case: Optional[TestCase],
    anchor_created_at_ms: Optional[int],
) -> list[dict]:
    if not app_identifier or not case or anchor_created_at_ms is None:
        return []

    from api.v1.sessions import _DIDI_COMPLEX_TRANSACTION_CODES

    correlation_tokens = _case_correlation_tokens(case)
    txn_code = infer_transaction_code(case.request_body) if case.request_body else None
    tra_id = _extract_xml_tag_text(case.request_body, "tra_id", "traId")
    didi_complex = txn_code in _DIDI_COMPLEX_TRANSACTION_CODES
    if not didi_complex and not correlation_tokens:
        return []

    result = await db.execute(
        select(ArexMocker)
        .where(
            ArexMocker.app_id == app_identifier,
            ArexMocker.category_name == "Servlet",
            ArexMocker.is_entry_point.is_(True),
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
            if _entrypoint_mocker_matches_case(mocker, case):
                continue

            parsed_endpoint = urlparse(endpoint)
            if endpoint.startswith("/internal/didi/"):
                if not didi_complex:
                    continue
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
            else:
                sibling_text = _sibling_mocker_correlation_text(mocker)
                if not any(token and token in sibling_text for token in correlation_tokens):
                    continue

            sub_call = _build_http_sub_call_from_sibling_servlet(mocker)
            if sub_call is not None:
                sibling_sub_calls.append(sub_call)
        except Exception as exc:
            logger.warning("Failed to parse sibling Servlet ArexMocker %s: %s", row.id, exc)

    return sibling_sub_calls


async def register_ws(job_id: int, ws):
    async with _ws_connections_lock:
        _ws_connections.setdefault(job_id, set()).add(ws)


async def unregister_ws(job_id: int, ws):
    async with _ws_connections_lock:
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
    async with database.async_session_factory() as db:
        app_identifier = None
        case_application_id = getattr(case, "application_id", None) if case else None
        if case_application_id:
            app_result = await db.execute(
                select(Application).where(Application.id == case_application_id)
            )
            app = app_result.scalar_one_or_none()
            if app:
                app_identifier = app.arex_app_id or app.name
            if hasattr(db, "rollback"):
                await db.rollback()

        mockers = []
        if record_id:
            await asyncio.sleep(_AREX_AGENT_FLUSH_DELAY_S)
            mockers = await _load_sub_call_mockers(db, record_id)
            _sub_call_query = (
                select(ArexMocker)
                .where(
                    ArexMocker.record_id == record_id,
                    ArexMocker.is_entry_point.is_(False),
                )
                .order_by(ArexMocker.id)
            )
            # Retry when AREX agent hasn't flushed sub-calls yet
            for _retry in range(settings.arex_flush_max_retries):
                if mockers:
                    break
                if hasattr(db, "rollback"):
                    await db.rollback()
                await asyncio.sleep(settings.arex_flush_retry_interval_s)
                result = await db.execute(_sub_call_query)
                mockers = result.scalars().all()
                if not mockers:
                    logger.debug(
                        "AREX sub-calls still empty after retry %d/%d for record_id=%s",
                        _retry + 1, settings.arex_flush_max_retries, record_id,
                    )

        if not mockers:
            if hasattr(db, "rollback"):
                await db.rollback()
            fallback_record_id = await _find_recent_entry_record_id(
                db,
                app_identifier=app_identifier,
                case=case,
                anchor_created_at_ms=anchor_created_at_ms,
            )
            if fallback_record_id and fallback_record_id != record_id:
                logger.info(
                    "Recovered replay sub-call record_id by entry lookup: original=%s fallback=%s",
                    record_id or "<missing>",
                    fallback_record_id,
                )
                mockers = await _load_sub_call_mockers(db, fallback_record_id)
                record_id = fallback_record_id

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
                generic_database_sub_call = normalize_generic_database_sub_call(mocker, cat_name or m.category_name)
                if generic_database_sub_call is not None:
                    sub_calls.append(generic_database_sub_call)
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
    sub_call_diff_detail: Optional[str] = None,
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
        replay_result.sub_call_diff_detail = sub_call_diff_detail

        await db.commit()
        await db.refresh(replay_result)
        return replay_result
