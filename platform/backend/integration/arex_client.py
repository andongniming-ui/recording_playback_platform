"""
AREX Storage REST API client.
Replaces repeater_client.py — no Hessian, no SFTP, pure async HTTP.
"""
import httpx
from datetime import datetime

from utils.timezone import ensure_beijing_datetime


class ArexClientError(Exception):
    """Raised when arex-storage returns non-200 or a network error occurs."""
    pass


class ArexClient:
    """Async HTTP client for arex-storage REST API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    async def query_recordings(
        self,
        app_id: str,
        begin_time: datetime,
        end_time: datetime,
        page_size: int = 50,
        page_index: int = 0,
    ) -> dict:
        """
        Query recordings for an app in a time range.
        POST /api/storage/replay/query/replayCase
        Returns full JSON response dict from arex-storage.
        """
        body = {
            "appId": app_id,
            "beginTime": self._to_epoch_ms(begin_time),
            "endTime": self._to_epoch_ms(end_time),
            "pageSize": page_size,
            "pageIndex": page_index,
            # arex-storage 0.6.x requires 'category' for Servlet entry recordings
            "category": {"name": "Servlet", "entryPoint": True, "skipComparison": False},
        }
        return await self._post("/api/storage/replay/query/replayCase", body)

    async def view_recording(self, record_id: str) -> dict:
        """
        Get full details of a recording including targetResponse.
        arex-storage 0.6.x: POST /api/storage/replay/query/viewRecord with {"recordId": ...}
        Returns the first Servlet entry in recordResult, or the full response dict.
        """
        resp = await self._post(
            "/api/storage/replay/query/viewRecord",
            {"recordId": record_id},
        )
        # arex-storage 0.6.x returns {"recordResult": [...], "desensitized": false}
        results = resp.get("recordResult") or []
        # Return the Servlet entry point record (entryPoint=true) if available
        for r in results:
            ct = r.get("categoryType", {})
            if isinstance(ct, dict) and ct.get("entryPoint"):
                return r
        return results[0] if results else {}

    async def count_recordings(
        self,
        app_id: str,
        begin_time: datetime,
        end_time: datetime,
    ) -> int:
        """
        Count recordings for an app in a time range.
        POST /api/storage/replay/query/countByRange
        Returns integer count, 0 if not present in response.
        """
        body = {
            "appId": app_id,
            "beginTime": self._to_epoch_ms(begin_time),
            "endTime": self._to_epoch_ms(end_time),
            "category": {"name": "Servlet", "entryPoint": True, "skipComparison": False},
        }
        resp = await self._post("/api/storage/replay/query/countByRange", body)
        # arex-storage 0.6.x: {"count": N} at top level
        if "count" in resp:
            return int(resp["count"])
        # Fallback for older shape: {"body": {"count": N}} or {"body": N}
        body_val = resp.get("body", {})
        if isinstance(body_val, dict):
            return int(body_val.get("count", 0))
        if isinstance(body_val, (int, float)):
            return int(body_val)
        return 0

    async def cache_load_mock(self, record_id: str, target_env: str = "") -> dict:
        """
        Preload mock sub-invocation data into Redis before replay.
        POST /api/storage/replay/query/cacheLoad
        """
        body = {"recordId": record_id, "targetEnv": target_env}
        return await self._post("/api/storage/replay/query/cacheLoad", body)

    async def cache_remove_mock(self, record_id: str) -> dict:
        """
        Remove mock data from Redis after replay.
        POST /api/storage/replay/query/cacheRemove
        """
        body = {"recordId": record_id}
        return await self._post("/api/storage/replay/query/cacheRemove", body)

    async def health_check(self) -> bool:
        """
        Check if arex-storage is reachable. Never raises.
        GET /api/storage/record/saveTest/
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/storage/record/saveTest/")
                return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _to_epoch_ms(dt: datetime) -> int:
        """Convert datetime to epoch milliseconds."""
        localized = ensure_beijing_datetime(dt)
        return int(localized.timestamp() * 1000) if localized else 0

    async def _post(self, path: str, body: dict) -> dict:
        """POST to arex-storage; raise ArexClientError on failure."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    url,
                    json=body,
                    headers={"Content-Type": "application/json"},
                )
        except httpx.RequestError as e:
            raise ArexClientError(f"Network error calling {url}: {e}") from e
        if resp.status_code != 200:
            raise ArexClientError(
                f"arex-storage POST {path} → {resp.status_code}: {resp.text[:200]}"
            )
        return resp.json()

    async def _get(self, path: str) -> dict:
        """GET from arex-storage; raise ArexClientError on failure."""
        url = f"{self.base_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(url)
        except httpx.RequestError as e:
            raise ArexClientError(f"Network error calling {url}: {e}") from e
        if resp.status_code != 200:
            raise ArexClientError(
                f"arex-storage GET {path} → {resp.status_code}: {resp.text[:200]}"
            )
        return resp.json()
