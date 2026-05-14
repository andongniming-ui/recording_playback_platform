"""
AREX Storage REST API client.
Replaces repeater_client.py — no Hessian, no SFTP, pure async HTTP.

Connection pool design
----------------------
Every call to  ``async with ArexClient(url) as c``  in the old code created a
brand-new httpx.AsyncClient and closed it on exit.  When the frontend polls
``GET /sessions?refresh_active_count=true`` every 10 s and there are 20+
active sessions, this produces hundreds of short-lived TCP connections per
minute, rapidly exhausting the process's file-descriptor limit (Errno 24:
Too many open files) and taking down the whole uvicorn worker.

The fix is a module-level dict that maps ``base_url → httpx.AsyncClient``.
Instances are created on first use and **never closed inside a request**.
They are closed only during application shutdown via ``close_all_clients()``.

Usage
-----
* Short-lived context manager style (backward compatible):
    async with ArexClient(url) as client:
        result = await client.query_recordings(...)

* Long-lived singleton style (recommended in background tasks):
    client = ArexClient.get_shared(url)
    result = await client.query_recordings(...)

* Application shutdown (call from lifespan finally block):
    await ArexClient.close_all_clients()
"""
import httpx
from datetime import datetime, timezone
from typing import ClassVar


class ArexClientError(Exception):
    """Raised when arex-storage returns non-200 or a network error occurs."""
    pass


class ArexClient:
    """Async HTTP client for arex-storage REST API."""

    # ------------------------------------------------------------------ #
    # Global connection-pool registry (url → shared AsyncClient)
    # ------------------------------------------------------------------ #
    _pool: ClassVar[dict[str, "ArexClient"]] = {}

    @classmethod
    def get_shared(cls, base_url: str) -> "ArexClient":
        """Return (or lazily create) the shared ArexClient for *base_url*.

        The returned client is backed by a persistent httpx.AsyncClient that
        is reused across all callers.  It must NOT be closed by the caller —
        use ``close_all_clients()`` during application shutdown instead.
        """
        key = base_url.rstrip("/")
        if key not in cls._pool:
            instance = cls(key)
            instance._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_connections=20,
                    max_keepalive_connections=10,
                    keepalive_expiry=30,
                ),
            )
            cls._pool[key] = instance
        return cls._pool[key]

    @classmethod
    async def close_all_clients(cls) -> None:
        """Close every pooled httpx.AsyncClient.  Call once at app shutdown."""
        for instance in list(cls._pool.values()):
            if instance._client is not None:
                await instance._client.aclose()
                instance._client = None
        cls._pool.clear()

    # ------------------------------------------------------------------ #
    # Instance lifecycle
    # ------------------------------------------------------------------ #

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        # Track whether *this* instance owns its client (i.e. it was NOT
        # obtained via get_shared and should be closed on __aexit__).
        self._owns_client: bool = False

    async def __aenter__(self):
        if self._client is None:
            # Backward-compat: stand-alone ``async with ArexClient(url)`` use.
            # Create a private client that will be closed on __aexit__.
            self._client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(
                    max_connections=10,
                    max_keepalive_connections=5,
                    keepalive_expiry=30,
                ),
            )
            self._owns_client = True
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._owns_client:
            await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self._owns_client = False

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
            client = self._get_client()
            resp = await client.get(f"{self.base_url}/api/storage/record/saveTest/")
            return resp.status_code == 200
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    def _get_client(self) -> httpx.AsyncClient:
        """Return the active httpx client, raising if not initialised."""
        if self._client is not None:
            return self._client
        # Caller forgot to use ``async with`` or ``get_shared`` — create a
        # temporary client so we don't crash, but warn in logs.
        import logging
        logging.getLogger(__name__).warning(
            "ArexClient._get_client called without an active httpx client "
            "(base_url=%s). Creating a temporary client — prefer using "
            "ArexClient.get_shared() or 'async with ArexClient(url)' instead.",
            self.base_url,
        )
        self._client = httpx.AsyncClient(timeout=30.0)
        self._owns_client = True
        return self._client

    @staticmethod
    def _to_epoch_ms(dt: datetime) -> int:
        """Convert datetime to epoch milliseconds."""
        if dt.tzinfo is None:
            localized = dt.replace(tzinfo=timezone.utc)
        else:
            localized = dt.astimezone(timezone.utc)
        return int(localized.timestamp() * 1000)

    async def _post(self, path: str, body: dict) -> dict:
        """POST to arex-storage; raise ArexClientError on failure."""
        url = f"{self.base_url}{path}"
        try:
            resp = await self._get_client().post(
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
            resp = await self._get_client().get(url)
        except httpx.RequestError as e:
            raise ArexClientError(f"Network error calling {url}: {e}") from e
        if resp.status_code != 200:
            raise ArexClientError(
                f"arex-storage GET {path} → {resp.status_code}: {resp.text[:200]}"
            )
        return resp.json()
