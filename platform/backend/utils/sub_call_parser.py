"""Generic sub-call parsing utilities.

Extracted from api/v1/sessions.py to break up the large sessions module.
These functions handle normalizing sub-call data regardless of source system.
"""

import json
import logging
import re

from utils.repository_capture import NOISE_DYNAMIC_CLASS_OPERATIONS

logger = logging.getLogger(__name__)


def _stringify_sub_call_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        return text or None
    try:
        return json.dumps(value, ensure_ascii=False)
    except Exception:
        return str(value)


def _normalize_recording_filter_prefixes(value) -> list[str]:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
        text = value.strip()
        if not text:
            return []
        lowered = text.lower()
        if any(marker in lowered for marker in ("re:", "regex:")) or (
            text.startswith("/") and text.endswith("/")
        ):
            parts = re.split(r"[\n;；]+", text)
        else:
            parts = re.split(r"[\n,，;；]+", text)
        return [part.strip() for part in parts if part.strip()]
    return [str(value).strip()] if str(value).strip() else []


def _matches_recording_filter(transaction_code: str | None, prefixes: list[str]) -> bool:
    normalized_tx = (transaction_code or "").strip()
    if not prefixes:
        return True
    if not normalized_tx:
        return False
    normalized_tx_upper = normalized_tx.upper()
    for raw_rule in prefixes:
        rule = (raw_rule or "").strip()
        if not rule:
            continue
        lowered = rule.lower()
        if lowered.startswith("exact:"):
            target = rule.split(":", 1)[1].strip()
            if target and normalized_tx_upper == target.upper():
                return True
            continue
        if rule.startswith("="):
            target = rule[1:].strip()
            if target and normalized_tx_upper == target.upper():
                return True
            continue
        if lowered.startswith("re:") or lowered.startswith("regex:"):
            pattern = rule.split(":", 1)[1].strip()
            if not pattern:
                continue
            try:
                if re.fullmatch(pattern, normalized_tx, flags=re.IGNORECASE):
                    return True
            except re.error:
                logger.warning("无效的录制过滤正则规则: %s", rule)
            continue
        if len(rule) >= 2 and rule.startswith("/") and rule.endswith("/"):
            pattern = rule[1:-1].strip()
            if not pattern:
                continue
            try:
                if re.fullmatch(pattern, normalized_tx, flags=re.IGNORECASE):
                    return True
            except re.error:
                logger.warning("无效的录制过滤正则规则: %s", rule)
            continue
        if normalized_tx_upper.startswith(rule.upper()):
            return True
    return False


def _extract_sub_call_scalar(item: dict, keys: tuple[str, ...]):
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


def _extract_sub_call_children(item: dict) -> list[dict] | None:
    for key in ("children", "subCalls", "subInvocations", "sub_invocations", "items"):
        nested = item.get(key)
        if isinstance(nested, list) and nested:
            return [_normalize_sub_call_item(child) for child in nested if child is not None]
    return None


def _normalize_sub_call_item(item):
    if isinstance(item, dict):
        call_type = (
            item.get("type")
            or item.get("callType")
            or item.get("category")
            or item.get("subCallType")
            or item.get("invocationType")
            or item.get("name")
            or "UNKNOWN"
        )
        request_value = _extract_sub_call_scalar(
            item,
            ("request", "sql", "statement", "command", "query", "body", "detail", "params", "arguments"),
        )
        response_value = _extract_sub_call_scalar(
            item,
            ("response", "result", "returnValue", "output", "responseBody", "value", "rows"),
        )
        target_value = _extract_sub_call_scalar(item, ("target", "db", "service", "host", "endpoint", "datasource"))
        sql_value = _extract_sub_call_scalar(item, ("sql", "statement", "query"))
        params_value = _extract_sub_call_scalar(item, ("params", "parameters", "args", "arguments"))
        database_value = _extract_sub_call_scalar(item, ("database", "dbName", "schema", "catalog", "datasource"))
        operation_value = _extract_sub_call_scalar(item, ("operation", "operationName", "methodName", "action", "command"))
        table_value = _extract_sub_call_scalar(item, ("table", "tableName", "collection"))
        method_value = _extract_sub_call_scalar(item, ("method", "httpMethod", "rpcMethod", "verb"))
        endpoint_value = _extract_sub_call_scalar(item, ("endpoint", "path", "uri", "url"))
        elapsed_value = (
            item.get("elapsed_ms")
            or item.get("elapsedMs")
            or item.get("duration")
            or item.get("cost")
            or item.get("latencyMs")
            or item.get("elapsed")
        )
        normalized = {
            "type": str(call_type).strip() or "UNKNOWN",
            "request": request_value if isinstance(request_value, (dict, list)) else _stringify_sub_call_value(request_value),
            "response": response_value if isinstance(response_value, (dict, list)) else _stringify_sub_call_value(response_value),
        }
        if target_value is not None:
            normalized["target"] = _stringify_sub_call_value(target_value)
        if database_value is not None:
            normalized["database"] = _stringify_sub_call_value(database_value)
        if operation_value is not None:
            normalized["operation"] = _stringify_sub_call_value(operation_value)
        if table_value is not None:
            normalized["table"] = _stringify_sub_call_value(table_value)
        if method_value is not None:
            normalized["method"] = _stringify_sub_call_value(method_value)
        if endpoint_value is not None:
            normalized["endpoint"] = _stringify_sub_call_value(endpoint_value)
        if isinstance(request_value, dict):
            sql_value = sql_value or request_value.get("sql") or request_value.get("statement") or request_value.get("query")
            params_value = params_value or request_value.get("params") or request_value.get("parameters") or request_value.get("args") or request_value.get("arguments")
        if sql_value is not None:
            normalized["sql"] = _stringify_sub_call_value(sql_value)
        if params_value is not None:
            normalized["params"] = params_value if isinstance(params_value, (dict, list)) else _stringify_sub_call_value(params_value)
        if elapsed_value is not None:
            try:
                normalized["elapsed_ms"] = float(elapsed_value)
            except (TypeError, ValueError):
                pass
        if item.get("status") is not None:
            normalized["status"] = _stringify_sub_call_value(item.get("status"))
        for canonical_key, aliases in (
            ("trace_id", ("trace_id", "traceId")),
            ("parent_id", ("parent_id", "parentId")),
            ("span_id", ("span_id", "spanId")),
            ("thread_name", ("thread_name", "threadName")),
            ("error", ("error", "error_message", "message")),
        ):
            value = _extract_sub_call_scalar(item, aliases)
            if value is not None:
                normalized[canonical_key] = _stringify_sub_call_value(value)
        children = _extract_sub_call_children(item)
        if children:
            normalized["children"] = children
        return normalized
    return {
        "type": "UNKNOWN",
        "request": _stringify_sub_call_value(item),
        "response": None,
    }


def _extract_sub_calls(detail: dict, raw: dict) -> list[dict]:
    candidate_keys = (
        "subCallInfo",
        "subCalls",
        "subCallList",
        "subInvocationList",
        "subInvocations",
        "sub_invocations",
    )

    def _maybe_parse(value):
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            for key in candidate_keys + ("items", "data"):
                nested = value.get(key)
                if isinstance(nested, list):
                    return nested
            return [value]
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
            except Exception:
                return None
            return _maybe_parse(parsed)
        return [value]

    for source in (detail, raw):
        for key in candidate_keys:
            normalized = _maybe_parse(source.get(key))
            if normalized:
                return _filter_noise_sub_calls(
                    [_normalize_sub_call_item(item) for item in normalized if item is not None]
                )
    return []


def _is_noise_sub_call(item: dict | None) -> bool:
    if not isinstance(item, dict):
        return False
    sub_type = str(item.get("type") or "").strip().lower()
    operation = str(item.get("operation") or item.get("operationName") or "").strip()
    if sub_type != "dynamicclass":
        return False
    return operation in NOISE_DYNAMIC_CLASS_OPERATIONS


def _filter_noise_sub_calls(items: list[dict] | None) -> list[dict]:
    if not items:
        return []
    filtered: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        normalized = dict(item)
        children = normalized.get("children")
        if isinstance(children, list):
            cleaned_children = _filter_noise_sub_calls(children)
            if cleaned_children:
                normalized["children"] = cleaned_children
            else:
                normalized.pop("children", None)
        if _is_noise_sub_call(normalized):
            continue
        filtered.append(normalized)
    return filtered
