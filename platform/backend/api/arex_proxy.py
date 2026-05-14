"""
Self-contained arex-storage proxy with local storage.

When AR_AREX_STORAGE_URL is empty, points to localhost, or points to 127.0.0.1,
all arex-storage API calls are handled locally using arex-recorder's own database.
No separate arex-storage-service is required.

When AR_AREX_STORAGE_URL points to an external host, the proxy forwards
agent calls to that URL (compatibility mode for existing arex-storage deployments).

AREX agent configuration:
  -Darex.storage.service.host=<arex-recorder-host>
  -Darex.storage.service.port=8000

Local endpoints handled natively:
  POST /api/storage/record/save
  POST /api/storage/record/batchSaveMockers
  GET  /api/storage/record/saveTest/
  POST /api/storage/replay/query/replayCase
  POST /api/storage/replay/query/viewRecord
  POST /api/storage/replay/query/countByRange
  POST /api/storage/replay/query/cacheLoad
  POST /api/storage/replay/query/cacheRemove
"""
import asyncio
import json
import logging
import secrets
import re
from collections import Counter
from datetime import datetime
from ipaddress import ip_address, ip_network
from urllib.parse import parse_qs, unquote, urlparse

import httpx
import zstandard as zstd
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.arex_mocker import ArexMocker
from utils.repository_capture import (
    get_dynamic_class_configurations,
    is_noise_dynamic_mocker,
    normalize_repository_sub_call,
)
from utils.timezone import now_beijing, from_epoch_ms_beijing

logger = logging.getLogger(__name__)
router = APIRouter()

SUCCESS_RESPONSE = b'{"responseStatusType":{"responseCode":0,"responseDesc":"success","timestamp":0}}'


# ── Helpers ───────────────────────────────────────────────────────────────────

def _log_info(message: str, *args) -> None:
    logger.info(message, *args)


def _log_warning(message: str, *args) -> None:
    logger.warning(message, *args)


def _decompress(data: bytes) -> bytes:
    """Try zstd decompress; fall back to raw bytes."""
    if not data:
        return data
    try:
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(data) as r:
            return r.read()
    except Exception:
        return data


def _is_proxy_mode() -> bool:
    """Return True when AR_AREX_STORAGE_URL points to an external arex-storage."""
    url = (settings.arex_storage_url or "").strip()
    if not url:
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").strip().lower()
    if not host:
        return False
    local_hosts = {
        "localhost",
        "127.0.0.1",
        "::1",
        "0.0.0.0",
        "backend",
        "arex-recorder-backend",
    }
    if host in local_hosts:
        return False
    try:
        if ip_address(host).is_loopback:
            return False
    except ValueError:
        pass
    return True


def _client_host(request: Request) -> str:
    return request.client.host if request.client else "-"


def _is_private_client_host(host: str) -> bool:
    if not host or host == "-":
        return False
    try:
        addr = ip_address(host)
    except ValueError:
        return False
    if addr.is_loopback or addr.is_private or addr.is_link_local:
        return True
    # Docker bridge networks are usually private, but keep this explicit for
    # older Python/ipaddress behavior and easier operator reasoning.
    return any(addr in network for network in (
        ip_network("10.0.0.0/8"),
        ip_network("172.16.0.0/12"),
        ip_network("192.168.0.0/16"),
    ))


async def _require_agent_ingest_allowed(request: Request) -> None:
    host = _client_host(request)
    if settings.arex_proxy_allow_private_only and not _is_private_client_host(host):
        logger.warning("[arex_proxy] rejected non-private agent ingest client=%s", host)
        raise HTTPException(status_code=403, detail="Agent ingest is restricted to private networks")

    expected = (settings.arex_agent_shared_secret or "").strip()
    if expected:
        provided = (
            request.headers.get("x-arex-agent-secret")
            or request.headers.get("x-agent-secret")
            or ""
        ).strip()
        if not secrets.compare_digest(provided, expected):
            logger.warning("[arex_proxy] rejected agent ingest with invalid secret client=%s", host)
            raise HTTPException(status_code=401, detail="Invalid agent secret")


def _truncate(value, limit: int = 240) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
    else:
        try:
            text = json.dumps(value, ensure_ascii=False)
        except Exception:
            text = str(value).strip()
    if not text:
        return None
    return text if len(text) <= limit else f"{text[:limit]}..."


def _parse_body_json_or_text(value):
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    if not isinstance(value, str):
        return value
    text = value.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


def _extract_txn_fields_from_text(text: str | None) -> dict[str, str]:
    if not text:
        return {}

    pairs: dict[str, str] = {}
    for field in ("tra_id", "request_no", "txn_code", "code", "biz_code"):
        match = re.search(rf"<{field}>([^<]+)</{field}>", text)
        if match:
            pairs[field] = match.group(1).strip()
    return pairs


def _extract_http_context(mocker: dict) -> tuple[str | None, dict[str, str], str | None]:
    target_request = mocker.get("targetRequest") or {}
    request_body = target_request.get("body") if isinstance(target_request, dict) else None
    request_payload = _parse_body_json_or_text(request_body)
    attrs = target_request.get("attributes") or {}
    request_path = attrs.get("RequestPath") or attrs.get("requestPath") or mocker.get("operationName")
    http_method = attrs.get("HttpMethod") or attrs.get("httpMethod")

    context: dict[str, str] = {}
    if isinstance(request_payload, str):
        context.update(_extract_txn_fields_from_text(request_payload))
    elif isinstance(request_payload, dict):
        for key in ("traId", "tra_id", "requestNo", "request_no", "txnCode", "txn_code", "code", "biz_code"):
            value = request_payload.get(key)
            if value not in (None, ""):
                context[key] = str(value)

    if request_path:
        parsed = urlparse(request_path)
        query_params = parse_qs(parsed.query)
        for key in ("traId", "requestNo", "txnCode", "code", "bizCode", "plateNo"):
            value = query_params.get(key)
            if value and value[0]:
                context[key] = unquote(value[0])

    request_summary = _truncate(request_payload)
    if request_path and http_method:
        request_summary = f"{http_method} {request_path}" + (f", body={request_summary}" if request_summary else "")
    elif request_path:
        request_summary = request_path + (f", body={request_summary}" if request_summary else "")

    target_response = mocker.get("targetResponse") or {}
    response_body = target_response.get("body") if isinstance(target_response, dict) else None
    response_summary = _truncate(_parse_body_json_or_text(response_body))
    return request_summary, context, response_summary


def _extract_repository_context(mocker: dict) -> tuple[str | None, dict[str, str], str | None]:
    normalized = normalize_repository_sub_call(mocker, str((mocker.get("categoryType") or {}).get("name") or ""))
    if not normalized:
        return None, {}, None

    params = normalized.get("params")
    request = normalized.get("request")
    response = normalized.get("response")

    context: dict[str, str] = {}
    source = params if isinstance(params, dict) else request if isinstance(request, dict) else {}
    for key in ("requestNo", "txnCode", "plateNo", "customerNo", "policyNo", "claimNo", "garageCode", "status"):
        value = source.get(key) if isinstance(source, dict) else None
        if value not in (None, ""):
            context[key] = str(value)

    request_summary = (
        f"{normalized.get('operation')} "
        f"table={normalized.get('table')} "
        f"params={_truncate(params if params is not None else request)}"
    )
    response_summary = _truncate(response)
    return request_summary, context, response_summary


def _detail_lines_for_mockers(mockers: list[dict]) -> list[str]:
    details: list[str] = []
    for mocker in mockers:
        if not isinstance(mocker, dict):
            continue

        category = mocker.get("categoryType") or {}
        category_name = category if isinstance(category, str) else str(category.get("name") or "UNKNOWN")
        operation = str(mocker.get("operationName") or "").strip()
        record_id = str(mocker.get("recordId") or "").strip() or "-"

        if is_noise_dynamic_mocker(operation, category_name):
            continue

        if category_name in {"Servlet", "HttpClient"}:
            request_summary, context, response_summary = _extract_http_context(mocker)
        elif category_name == "DynamicClass":
            request_summary, context, response_summary = _extract_repository_context(mocker)
            if not request_summary:
                continue
        else:
            continue

        context_pairs = []
        for key in ("tra_id", "traId", "request_no", "requestNo", "txn_code", "txnCode", "code", "biz_code", "bizCode", "plateNo"):
            value = context.get(key)
            if value:
                context_pairs.append(f"{key}={value}")
        context_suffix = f" {' '.join(context_pairs)}" if context_pairs else ""
        response_suffix = f" response={response_summary}" if response_summary else ""
        details.append(
            f"[arex_proxy] detail record_id={record_id} type={category_name} op={operation or '-'}"
            f"{context_suffix} request={request_summary or '-'}{response_suffix}"
        )
    return details[:10]


def _summarize_mockers(mockers: list[dict]) -> dict:
    app_ids: set[str] = set()
    record_ids: list[str] = []
    categories: Counter[str] = Counter()
    operations: list[str] = []
    entry_points = 0

    for mocker in mockers:
        if not isinstance(mocker, dict):
            continue
        app_id = str(mocker.get("appId") or "").strip()
        if app_id:
            app_ids.add(app_id)

        record_id = str(mocker.get("recordId") or mocker.get("id") or "").strip()
        if record_id and record_id not in record_ids and len(record_ids) < 5:
            record_ids.append(record_id)

        category = mocker.get("categoryType") or {}
        if isinstance(category, str):
            category_name = category
            is_entry_point = False
        else:
            category_name = str(category.get("name") or "UNKNOWN")
            is_entry_point = bool(category.get("entryPoint", False))
        categories[category_name] += 1
        entry_points += int(is_entry_point)

        operation = str(mocker.get("operationName") or "").strip()
        if operation and operation not in operations and len(operations) < 5:
            operations.append(operation)

    return {
        "count": len(mockers),
        "entry_points": entry_points,
        "app_ids": sorted(app_ids),
        "record_ids": record_ids,
        "categories": dict(categories),
        "operations": operations,
    }


def _summarize_config_body(body: dict | None) -> dict:
    body = body if isinstance(body, dict) else {}
    app_id = str(body.get("appId") or body.get("id") or body.get("serviceName") or "").strip()
    agent_status = (
        body.get("agentStatus")
        or body.get("status")
        or body.get("agentState")
        or body.get("state")
    )
    host = body.get("host") or body.get("hostName") or body.get("hostname")
    return {
        "app_id": app_id or "-",
        "agent_status": str(agent_status) if agent_status not in (None, "") else "-",
        "host": str(host) if host not in (None, "") else "-",
        "keys": sorted(body.keys())[:8],
    }


_proxy_client: httpx.AsyncClient | None = None
_proxy_client_lock = asyncio.Lock()


async def _get_proxy_client() -> httpx.AsyncClient:
    global _proxy_client
    if _proxy_client is not None and not _proxy_client.is_closed:
        return _proxy_client
    async with _proxy_client_lock:
        if _proxy_client is not None and not _proxy_client.is_closed:
            return _proxy_client
        _proxy_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
        )
        return _proxy_client


async def _close_proxy_client() -> None:
    global _proxy_client
    if _proxy_client is not None:
        await _proxy_client.aclose()
        _proxy_client = None


async def _proxy(request: Request, path: str) -> Response:
    """Forward request as-is to external arex-storage."""
    target_url = f"{settings.arex_storage_url}{path}"
    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    try:
        client = await _get_proxy_client()
        resp = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers,
        )
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            media_type=resp.headers.get("content-type"),
        )
    except Exception as e:
        return Response(content=f"Proxy error: {e}".encode(), status_code=502)


async def _store_mocker(mocker: dict, db: AsyncSession) -> None:
    """Parse and store a single AREX mocker into the local DB (no commit)."""
    record_id = mocker.get("recordId") or mocker.get("id")
    app_id = mocker.get("appId") or ""
    if not record_id:
        return

    category = mocker.get("categoryType") or {}
    if isinstance(category, str):
        category_name = category
        is_entry_point = False
    else:
        category_name = category.get("name") or ""
        is_entry_point = bool(category.get("entryPoint", False))

    created_at_ms = mocker.get("creationTime")
    if created_at_ms is not None:
        try:
            created_at_ms = int(created_at_ms)
        except (ValueError, TypeError):
            created_at_ms = None
    created_at = from_epoch_ms_beijing(created_at_ms) if created_at_ms is not None else now_beijing()

    db.add(ArexMocker(
        record_id=str(record_id),
        app_id=str(app_id),
        category_name=category_name,
        is_entry_point=is_entry_point,
        mocker_data=json.dumps(mocker, ensure_ascii=False),
        created_at_ms=created_at_ms,
        created_at=created_at,
    ))


# ── Health check ──────────────────────────────────────────────────────────────

@router.get("/api/storage/record/saveTest/")
async def health_check():
    return {"responseStatusType": {"responseCode": 0, "responseDesc": "success"}}


# ── Save endpoints ────────────────────────────────────────────────────────────

@router.post("/api/storage/record/save")
async def save_mocker(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/record/save")

    body = await request.body()
    decompressed = _decompress(body)
    try:
        mocker = json.loads(decompressed)
    except Exception as e:
        _log_warning("[arex_proxy] save parse error: %s", e)
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    summary = _summarize_mockers([mocker])
    _log_info(
        "[arex_proxy] save client=%s count=%d entry_points=%d apps=%s categories=%s record_ids=%s operations=%s",
        _client_host(request),
        summary["count"],
        summary["entry_points"],
        summary["app_ids"],
        summary["categories"],
        summary["record_ids"],
        summary["operations"],
    )
    for detail in _detail_lines_for_mockers([mocker]):
        _log_info("%s", detail)
    try:
        await _store_mocker(mocker, db)
        await db.commit()
    except Exception as exc:
        _log_warning("[arex_proxy] save commit failed (record_id=%s): %s", mocker.get("recordId"), exc)
        await db.rollback()
    return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")


@router.post("/api/storage/record/batchSaveMockers")
async def batch_save_mockers(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    raw = await request.body()
    decompressed = _decompress(raw)

    try:
        parsed = json.loads(decompressed)
    except Exception as e:
        _log_warning("[arex_proxy] batchSaveMockers parse error: %s, raw=%s", e, raw[:100])
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    if isinstance(parsed, list):
        mockers = parsed
    elif isinstance(parsed, dict):
        mockers = parsed.get("mockerList") or parsed.get("list") or [parsed]
    else:
        mockers = [parsed]

    summary = _summarize_mockers(mockers)
    _log_info(
        "[arex_proxy] batchSaveMockers client=%s count=%d entry_points=%d apps=%s categories=%s record_ids=%s operations=%s",
        _client_host(request),
        summary["count"],
        summary["entry_points"],
        summary["app_ids"],
        summary["categories"],
        summary["record_ids"],
        summary["operations"],
    )
    for detail in _detail_lines_for_mockers(mockers):
        _log_info("%s", detail)

    if _is_proxy_mode():
        # Proxy mode: forward mockers concurrently to arex-storage
        save_url = f"{settings.arex_storage_url}/api/storage/record/save"
        errors: list[str] = []
        _concurrency = 20

        async def _forward_one(mocker: dict, client: httpx.AsyncClient) -> None:
            try:
                resp = await client.post(
                    save_url,
                    json=mocker,
                    headers={"Content-Type": "application/json"},
                )
                if resp.status_code != 200:
                    errors.append(f"{mocker.get('recordId','?')}: {resp.status_code}")
            except Exception as e:
                logger.warning("[arex_proxy] batchSaveMockers forward failed for %s: %s", mocker.get("recordId", "?"), e)
                errors.append(str(e))

        sem = asyncio.Semaphore(_concurrency)
        async def _forward_with_limit(mocker: dict, client: httpx.AsyncClient) -> None:
            async with sem:
                await _forward_one(mocker, client)

        async with httpx.AsyncClient(timeout=30.0, limits=httpx.Limits(max_connections=_concurrency)) as client:
            tasks = [_forward_with_limit(m, client) for m in mockers]
            await asyncio.gather(*tasks)

        if errors:
            logger.warning("[arex_proxy] batchSaveMockers proxy: %d/%d forward errors: %s", len(errors), len(mockers), errors[:5])
            return Response(
                content=json.dumps({
                    "responseStatusType": {"responseCode": 1, "responseDesc": str(errors)}
                }).encode(),
                status_code=200,
                media_type="application/json",
            )
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    # Local mode: store all mockers directly
    try:
        for mocker in mockers:
            await _store_mocker(mocker, db)
        await db.commit()
    except Exception as exc:
        record_ids = [str(m.get("recordId", "?")) for m in mockers[:3]]
        _log_warning("[arex_proxy] batchSaveMockers commit failed (record_ids=%s): %s", record_ids, exc)
        await db.rollback()
    return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")


# ── Query endpoints (used by sessions.py sync) ────────────────────────────────

@router.post("/api/storage/replay/query/replayCase")
async def query_replay_case(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/replayCase")

    body = await request.json()
    app_id = body.get("appId", "")
    begin_time_ms = body.get("beginTime")
    end_time_ms = body.get("endTime") or int(now_beijing().timestamp() * 1000)
    page_size = int(body.get("pageSize") or 50)
    page_index = int(body.get("pageIndex") or 0)

    stmt = (
        select(ArexMocker)
        .where(
            ArexMocker.app_id == app_id,
            ArexMocker.is_entry_point.is_(True),
        )
        .order_by(ArexMocker.created_at_ms.desc())
        .offset(page_index * page_size)
        .limit(page_size)
    )
    if begin_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms >= int(begin_time_ms))
    if end_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms <= int(end_time_ms))

    result = await db.execute(stmt)
    records = []
    for m in result.scalars().all():
        try:
            records.append(json.loads(m.mocker_data))
        except Exception:
            pass

    return {"records": records}


@router.post("/api/storage/replay/query/viewRecord")
async def view_record(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/viewRecord")

    body = await request.json()
    record_id = body.get("recordId", "")

    result = await db.execute(
        select(ArexMocker).where(ArexMocker.record_id == record_id)
    )
    record_result = []
    for m in result.scalars().all():
        try:
            record_result.append(json.loads(m.mocker_data))
        except Exception:
            pass

    return {"recordResult": record_result, "desensitized": False}


@router.post("/api/storage/replay/query/countByRange")
async def count_by_range(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/countByRange")

    body = await request.json()
    app_id = body.get("appId", "")
    begin_time_ms = body.get("beginTime")
    end_time_ms = body.get("endTime") or int(now_beijing().timestamp() * 1000)

    stmt = select(func.count()).select_from(ArexMocker).where(
        ArexMocker.app_id == app_id,
        ArexMocker.is_entry_point.is_(True),
    )
    if begin_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms >= int(begin_time_ms))
    if end_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms <= int(end_time_ms))

    result = await db.execute(stmt)
    return {"count": result.scalar_one()}


@router.post("/api/storage/replay/query/cacheLoad")
async def cache_load(request: Request, db: AsyncSession = Depends(get_db)):
    await _require_agent_ingest_allowed(request)
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/cacheLoad")

    body = await request.json()
    record_id = body.get("recordId", "")

    result = await db.execute(
        select(ArexMocker).where(
            ArexMocker.record_id == record_id,
            ArexMocker.is_entry_point.is_(False),
        )
    )
    sub_calls = []
    for m in result.scalars().all():
        try:
            sub_calls.append(json.loads(m.mocker_data))
        except Exception:
            pass

    return {
        "responseStatusType": {"responseCode": 0, "responseDesc": "success"},
        "body": sub_calls,
    }


@router.post("/api/storage/replay/query/cacheRemove")
async def cache_remove(request: Request):
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/cacheRemove")
    # Local mode: nothing to clean up
    return {"responseStatusType": {"responseCode": 0, "responseDesc": "success"}}


# ── Config service endpoints (AREX agent initialization) ─────────────────────
# Agent calls these to fetch recording configuration on startup.
# In local mode we return a minimal "recording enabled" response so the
# agent activates its Servlet/JDBC interceptors without a separate config service.

@router.api_route("/api/config/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_config(request: Request, path: str):
    if _is_proxy_mode():
        return await _proxy(request, f"/api/config/{path}")

    # Local mode: extract appId and return a valid "recording enabled" config
    app_id = ""
    raw_body = await request.body()
    try:
        body = await request.json()
        app_id = body.get("appId") or body.get("id") or ""
    except Exception:
        body = {}
    config_summary = _summarize_config_body(body)
    _log_info(
        "[arex_proxy] config client=%s path=%s app_id=%s agent_status=%s host=%s keys=%s",
        _client_host(request),
        path,
        config_summary["app_id"] or app_id or "-",
        config_summary["agent_status"],
        config_summary["host"],
        config_summary["keys"],
    )

    # agentStatus: agent is reporting status, just ack it
    if "agentStatus" in path:
        return {
            "responseStatusType": {"responseCode": 0, "responseDesc": "success", "timestamp": 0},
        }

    # agent/load is the main config load URI (CONFIG_LOAD_URI in ConfigService).
    # queryConfigOfAgent and all other config paths also use this same response format.
    # ResponseBody fields: status, agentEnabled, serviceCollectConfiguration, dynamicClassConfigurationList
    return {
        "responseStatusType": {"responseCode": 0, "responseDesc": "success", "timestamp": 0},
        "body": {
            "status": 1,
            "agentEnabled": True,
            "serviceCollectConfiguration": {
                "appId": app_id,
                "sampleRate": 100,
                "allowDayOfWeeks": 127,
                "allowTimeOfDayFrom": "00:01",
                "allowTimeOfDayTo": "23:59",
                "timeMock": False,
                "excludeServiceOperationSet": [],
            },
            "dynamicClassConfigurationList": get_dynamic_class_configurations(),
        },
    }


# ── Transparent proxy for all other arex-storage calls ───────────────────────

@router.api_route("/api/storage/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_storage(request: Request, path: str):
    return await _proxy(request, f"/api/storage/{path}")
