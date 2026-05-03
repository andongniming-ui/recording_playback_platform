"""AREX recording payload parsing helpers.

These helpers are intentionally free of database and FastAPI dependencies so
recording sync code can reuse them without growing the sessions router.
"""

import base64
import json


HTTP_METHODS = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}


def extract_records_from_query_response(data) -> list[dict]:
    records_raw: list[dict] = []
    if isinstance(data, dict):
        if "records" in data:
            records_raw = data["records"] or []
        else:
            body_val = data.get("body")
            if isinstance(body_val, list):
                records_raw = body_val
            elif isinstance(body_val, dict):
                records_raw = (
                    body_val.get("records")
                    or body_val.get("recordResult")
                    or body_val.get("recordList")
                    or body_val.get("sources")
                    or []
                )
            if not records_raw:
                records_raw = data.get("recordResult") or []
    return [item for item in records_raw if isinstance(item, dict)]


def extract_request_meta(detail: dict, raw: dict) -> tuple[str, str]:
    # arex-storage 0.4.x/0.6.x stores method in targetRequest.attributes.HttpMethod
    def _attrs_method(d: dict) -> str | None:
        target_request = d.get("targetRequest") or {}
        attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
        return attrs.get("HttpMethod") or attrs.get("httpMethod")

    def _attrs_path(d: dict) -> str | None:
        target_request = d.get("targetRequest") or {}
        attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
        return attrs.get("RequestPath") or attrs.get("requestPath")

    method_candidates = [
        _attrs_method(detail),
        _attrs_method(raw),
        detail.get("requestMethod"),
        raw.get("requestMethod"),
    ]
    uri_candidates = [
        _attrs_path(detail),
        _attrs_path(raw),
        detail.get("requestUri"),
        raw.get("requestUri"),
        detail.get("uri"),
        raw.get("uri"),
    ]
    operation_name = detail.get("operationName") or raw.get("operationName") or ""
    if operation_name:
        first, sep, rest = operation_name.partition(" ")
        if sep and first.upper() in HTTP_METHODS:
            method_candidates.append(first.upper())
            uri_candidates.append(rest.strip())
        else:
            uri_candidates.append(operation_name)

    method = next((str(value).upper() for value in method_candidates if value), "GET")
    uri = next((str(value).strip() for value in uri_candidates if value), "/")
    return method, uri


def is_probable_internal_servlet_record(raw: dict) -> bool:
    """AREX also records internal HTTP sub-invocations as Servlet entries."""
    _, request_uri = extract_request_meta(raw, raw)
    return request_uri.startswith("/internal/") or request_uri.startswith("/api/internal/")


def decode_body(value) -> str | None:
    """Decode arex-storage request/response body.

    arex agent stores raw bytes as Base64 in targetRequest / targetResponse
    bodies. Decode to UTF-8 text when possible; otherwise preserve the value.
    """
    if value is None:
        return None
    if not isinstance(value, str):
        return json.dumps(value)
    try:
        return base64.b64decode(value).decode("utf-8")
    except Exception:
        return value


def serialize_payload(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value)


def extract_request_headers(detail: dict) -> str | None:
    target_request = detail.get("targetRequest") or {}
    attrs = (target_request.get("attributes") or {}) if isinstance(target_request, dict) else {}
    headers = attrs.get("Headers") or detail.get("requestHeaders") or {}
    return serialize_payload(headers)


def extract_request_body(detail: dict) -> str | None:
    target_request = detail.get("targetRequest")
    if isinstance(target_request, dict):
        body = target_request.get("body")
    else:
        body = target_request
    return decode_body(body or detail.get("requestBody"))


def extract_response_body(detail: dict) -> str | None:
    target_response = detail.get("targetResponse")
    if isinstance(target_response, dict):
        body = target_response.get("body")
    else:
        body = target_response
    return decode_body(body or detail.get("responseBody"))


# Backward-compatible aliases for older internal tests/imports.
_extract_records_from_query_response = extract_records_from_query_response
_extract_request_meta = extract_request_meta
_is_probable_internal_servlet_record = is_probable_internal_servlet_record
_decode_body = decode_body
_serialize_payload = serialize_payload
_extract_request_headers = extract_request_headers
_extract_request_body = extract_request_body
_extract_response_body = extract_response_body
