"""
Sub-call matching and normalization utilities.

Consolidated from duplicated logic in api/v1/replays.py and core/replay_executor.py.
"""
import json
import re
from urllib.parse import urlparse


def normalize_sub_call_type(value) -> str:
    """Normalize a sub-call type string to a canonical form."""
    type_name = str(value or "").strip().lower()
    if not type_name:
        return ""
    if "http" in type_name:
        return "http"
    if "mysql" in type_name or "jdbc" in type_name or "database" in type_name:
        return "database"
    return type_name


def normalize_http_operation(operation: str) -> str:
    """Normalize an HTTP sub-call operation string (e.g. 'GET /api/foo')."""
    text = re.sub(r"\s+", " ", str(operation or "").strip())
    if not text:
        return ""
    parts = text.split(" ", 1)
    if len(parts) == 2 and parts[0].isalpha():
        method = parts[0].upper()
        target = parts[1].strip()
    else:
        method = ""
        target = text
    parsed = urlparse(target)
    path = parsed.path or target.split("?", 1)[0] or target
    return f"{method} {path}".strip().lower()


def normalize_sub_call_operation(item: dict | None) -> str:
    """Normalize a sub-call item's operation field."""
    if not isinstance(item, dict):
        return ""
    operation = str(item.get("operation") or "").strip()
    if not operation:
        return ""
    if normalize_sub_call_type(item.get("type")) == "http":
        return normalize_http_operation(operation)
    return re.sub(r"\s+", " ", operation).lower()


def normalize_sub_call_value(value) -> str:
    """Normalize a sub-call request/response value to a comparable string."""
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return ""
        try:
            return json.dumps(json.loads(text), ensure_ascii=False, sort_keys=True)
        except Exception:
            return re.sub(r"\s+", " ", text)
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value).strip()


def parse_sub_call_payload(value):
    """Parse a sub-call payload that may be a JSON string."""
    if isinstance(value, str):
        text = value.strip()
        if len(text) >= 2 and (
            (text.startswith("{") and text.endswith("}"))
            or (text.startswith("[") and text.endswith("]"))
            or (text.startswith('"') and text.endswith('"'))
        ):
            try:
                return parse_sub_call_payload(json.loads(text))
            except Exception:
                return value
    return value


def unwrap_sub_call_response(value):
    """Normalize fallback HttpClient wrappers before comparing responses."""
    parsed = parse_sub_call_payload(value)
    if (
        isinstance(parsed, dict)
        and "body" in parsed
        and set(parsed.keys()).issubset({"body", "httpStatus", "status", "statusCode", "headers"})
    ):
        return parse_sub_call_payload(parsed.get("body"))
    return parsed
