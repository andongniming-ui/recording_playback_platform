"""Sub-call fetching and reconstruction utilities for replay.

Extracted from core/replay_executor.py. These functions handle loading
sub-call mockers from DB, reconstructing sibling HTTP sub-calls, and
assembling the full sub-call list for a replay result.
"""

import asyncio
import json
import logging
import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select

from config import settings
import database
from models.application import Application
from models.arex_mocker import ArexMocker
from models.test_case import TestCase
from utils.repository_capture import (
    is_noise_dynamic_mocker,
    normalize_generic_database_sub_call,
    normalize_repository_sub_call,
)
from utils.system_plugin import get_plugin_for_app_id
from utils.sub_call_merge import merge_sub_calls, exclude_duplicate_database_sub_calls

logger = logging.getLogger(__name__)

_SIBLING_SERVLET_LOOKAROUND_MS = 5000
_REPLAY_ENTRY_LOOKAROUND_MS = 10000


# ---------------------------------------------------------------------------
# Small pure helpers used by sub-call fetch logic
# ---------------------------------------------------------------------------

def _decode_possible_base64_text(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    try:
        decoded = value.encode("utf-8")  # ensure bytes first
        decoded = __import__("base64").b64decode(decoded, validate=True).decode("utf-8")
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


# ---------------------------------------------------------------------------
# Entrypoint / sibling-servlet matching
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Async DB queries for sub-call fetching
# ---------------------------------------------------------------------------

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

    correlation_tokens = _case_correlation_tokens(case)
    plugin = get_plugin_for_app_id(app_identifier)
    if plugin:
        should_fetch = plugin.should_fetch_sibling_http_sub_calls(case.request_body, correlation_tokens)
    else:
        should_fetch = bool(correlation_tokens)
    if not should_fetch:
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
            query_params = {
                key: values[-1]
                for key, values in parse_qs(parsed_endpoint.query, keep_blank_values=True).items()
                if values
            }
            sibling_text = _sibling_mocker_correlation_text(mocker)
            if plugin:
                matched = plugin.matches_sibling_http_sub_call(
                    endpoint=endpoint,
                    query_params=query_params,
                    request_body=case.request_body,
                    correlation_text=sibling_text,
                    correlation_tokens=correlation_tokens,
                )
            else:
                matched = any(token and token in sibling_text for token in correlation_tokens)
            if not matched:
                continue

            sub_call = _build_http_sub_call_from_sibling_servlet(mocker)
            if sub_call is not None:
                sibling_sub_calls.append(sub_call)
        except Exception as exc:
            logger.warning("Failed to parse sibling Servlet ArexMocker %s: %s", row.id, exc)

    return sibling_sub_calls


# ---------------------------------------------------------------------------
# Main sub-call fetch orchestrator
# ---------------------------------------------------------------------------

async def _fetch_replay_sub_calls(
    record_id: Optional[str],
    case: Optional[TestCase] = None,
    anchor_created_at_ms: Optional[int] = None,
    arex_flush_delay_s: float | None = None,
) -> Optional[str]:
    """Fetch replay sub-calls from AREX or fall back to app-specific reconstruction.

    When `record_id` is present, this waits for AREX agent flush and loads reported
    sub-calls for that replay record. When it is absent, only best-effort app-aware
    reconstruction is attempted through the plugin interface.
    """
    if arex_flush_delay_s is None:
        arex_flush_delay_s = settings.arex_flush_delay_s

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
            await asyncio.sleep(arex_flush_delay_s)
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
                    sub_calls = merge_sub_calls(sub_calls, missing_http_sub_calls)

            # Use plugin to fetch system-specific extra sub-calls
            plugin = get_plugin_for_app_id(
                app_identifier or next((m.app_id for m in mockers if m.app_id), "")
            )
            if plugin:
                plugin_sub_calls = await plugin.fetch_extra_sub_calls(
                    case.request_body if case else None,
                    app_identifier or next((m.app_id for m in mockers if m.app_id), ""),
                    None,
                    None,
                )
                if plugin_sub_calls:
                    sub_calls = exclude_duplicate_database_sub_calls(plugin_sub_calls, sub_calls)
                    sub_calls = merge_sub_calls(sub_calls, plugin_sub_calls)
        except Exception as exc:
            logger.warning("Failed to enrich replay sub-calls for %s: %s", record_id or "<missing>", exc)

    return json.dumps(sub_calls, ensure_ascii=False) if sub_calls else None
