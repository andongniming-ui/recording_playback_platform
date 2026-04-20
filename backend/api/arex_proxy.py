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
import json
import logging
from datetime import datetime, timezone

import httpx
import zstandard as zstd
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from models.arex_mocker import ArexMocker
from utils.repository_capture import get_dynamic_class_configurations

logger = logging.getLogger(__name__)
router = APIRouter()

SUCCESS_RESPONSE = b'{"responseStatusType":{"responseCode":0,"responseDesc":"success","timestamp":0}}'


# ── Helpers ───────────────────────────────────────────────────────────────────

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
    return not (url.startswith("http://localhost") or url.startswith("http://127.0.0.1"))


async def _proxy(request: Request, path: str) -> Response:
    """Forward request as-is to external arex-storage."""
    target_url = f"{settings.arex_storage_url}{path}"
    body = await request.body()
    headers = {
        k: v for k, v in request.headers.items()
        if k.lower() not in ("host", "content-length")
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
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


    db.add(ArexMocker(
        record_id=str(record_id),
        app_id=str(app_id),
        category_name=category_name,
        is_entry_point=is_entry_point,
        mocker_data=json.dumps(mocker, ensure_ascii=False),
        created_at_ms=created_at_ms,
    ))


# ── Health check ──────────────────────────────────────────────────────────────

@router.get("/api/storage/record/saveTest/")
async def health_check():
    return {"responseStatusType": {"responseCode": 0, "responseDesc": "success"}}


# ── Save endpoints ────────────────────────────────────────────────────────────

@router.post("/api/storage/record/save")
async def save_mocker(request: Request, db: AsyncSession = Depends(get_db)):
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/record/save")

    body = await request.body()
    decompressed = _decompress(body)
    try:
        mocker = json.loads(decompressed)
    except Exception as e:
        logger.warning("[arex_proxy] save parse error: %s", e)
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    await _store_mocker(mocker, db)
    await db.commit()
    return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")


@router.post("/api/storage/record/batchSaveMockers")
async def batch_save_mockers(request: Request, db: AsyncSession = Depends(get_db)):
    raw = await request.body()
    decompressed = _decompress(raw)

    try:
        parsed = json.loads(decompressed)
    except Exception as e:
        logger.warning("[arex_proxy] batchSaveMockers parse error: %s, raw=%s", e, raw[:100])
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    if isinstance(parsed, list):
        mockers = parsed
    elif isinstance(parsed, dict):
        mockers = parsed.get("mockerList") or parsed.get("list") or [parsed]
    else:
        mockers = [parsed]

    if _is_proxy_mode():
        # Proxy mode: forward each mocker individually to arex-storage
        save_url = f"{settings.arex_storage_url}/api/storage/record/save"
        errors = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for mocker in mockers:
                try:
                    resp = await client.post(
                        save_url,
                        json=mocker,
                        headers={"Content-Type": "application/json"},
                    )
                    if resp.status_code != 200:
                        errors.append(f"{mocker.get('recordId','?')}: {resp.status_code}")
                except Exception as e:
                    errors.append(str(e))

        if errors:
            return Response(
                content=json.dumps({
                    "responseStatusType": {"responseCode": 1, "responseDesc": str(errors)}
                }).encode(),
                status_code=200,
                media_type="application/json",
            )
        return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")

    # Local mode: store all mockers directly
    for mocker in mockers:
        await _store_mocker(mocker, db)
    await db.commit()
    return Response(content=SUCCESS_RESPONSE, status_code=200, media_type="application/json")


# ── Query endpoints (used by sessions.py sync) ────────────────────────────────

@router.post("/api/storage/replay/query/replayCase")
async def query_replay_case(request: Request, db: AsyncSession = Depends(get_db)):
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/replayCase")

    body = await request.json()
    app_id = body.get("appId", "")
    begin_time_ms = body.get("beginTime")
    end_time_ms = body.get("endTime") or int(datetime.now(timezone.utc).timestamp() * 1000)
    page_size = int(body.get("pageSize") or 50)
    page_index = int(body.get("pageIndex") or 0)

    stmt = (
        select(ArexMocker)
        .where(
            ArexMocker.app_id == app_id,
            ArexMocker.is_entry_point == True,  # noqa: E712
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
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/countByRange")

    body = await request.json()
    app_id = body.get("appId", "")
    begin_time_ms = body.get("beginTime")
    end_time_ms = body.get("endTime") or int(datetime.now(timezone.utc).timestamp() * 1000)

    stmt = select(func.count()).select_from(ArexMocker).where(
        ArexMocker.app_id == app_id,
        ArexMocker.is_entry_point == True,  # noqa: E712
    )
    if begin_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms >= int(begin_time_ms))
    if end_time_ms:
        stmt = stmt.where(ArexMocker.created_at_ms <= int(end_time_ms))

    result = await db.execute(stmt)
    return {"count": result.scalar_one()}


@router.post("/api/storage/replay/query/cacheLoad")
async def cache_load(request: Request, db: AsyncSession = Depends(get_db)):
    if _is_proxy_mode():
        return await _proxy(request, "/api/storage/replay/query/cacheLoad")

    body = await request.json()
    record_id = body.get("recordId", "")

    result = await db.execute(
        select(ArexMocker).where(
            ArexMocker.record_id == record_id,
            ArexMocker.is_entry_point == False,  # noqa: E712
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
    logger.info("[arex_proxy] config path=%s body=%s", path, raw_body[:500] if raw_body else b"")

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
