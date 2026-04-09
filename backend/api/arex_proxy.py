"""
Compatibility proxy for arex-agent 0.4.8 → arex-storage 0.6.x.

arex-agent 0.4.8 calls /api/storage/record/batchSaveMockers (batch endpoint)
arex-storage 0.6.x only supports /api/storage/record/save (single mocker).

This router:
- Intercepts POST /api/storage/record/batchSaveMockers, unpacks and forwards each mocker.
- Transparently proxies all other /api/storage/* and /api/config/* calls to arex-storage.

Set AR_AREX_AGENT_STORAGE_URL=http://172.25.109.28:8001 so agents talk to this backend.
"""
import json
import zstandard as zstd
import httpx
from fastapi import APIRouter, Request, Response
from config import settings

router = APIRouter()

SUCCESS_RESPONSE = b'{"responseStatusType":{"responseCode":0,"responseDesc":"success","timestamp":0}}'


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


async def _proxy(request: Request, path: str) -> Response:
    """Forward request as-is to arex-storage."""
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


# ── batchSaveMockers ─────────────────────────────────────────────────────────

@router.post("/api/storage/record/batchSaveMockers")
async def batch_save_mockers(request: Request):
    """
    Receive arex-agent 0.4.8 batch save; forward each mocker individually.
    Body: zstd-compressed JSON list of AREXMocker objects.
    """
    raw = await request.body()
    decompressed = _decompress(raw)
    try:
        parsed = json.loads(decompressed)
    except Exception as e:
        print(f"[arex_proxy] batchSaveMockers parse error: {e}, raw={raw[:100]}", flush=True)
        return await _proxy(request, "/api/storage/record/save")

    # Agent may send a list or a dict with a list inside
    if isinstance(parsed, list):
        mockers = parsed
    elif isinstance(parsed, dict):
        # Try common wrapper keys
        mockers = parsed.get("mockerList") or parsed.get("list") or [parsed]
    else:
        mockers = [parsed]

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


# ── Transparent proxy for all other arex-storage / arex-config calls ────────

@router.api_route("/api/storage/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_storage(request: Request, path: str):
    return await _proxy(request, f"/api/storage/{path}")


@router.api_route("/api/config/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_config(request: Request, path: str):
    return await _proxy(request, f"/api/config/{path}")
