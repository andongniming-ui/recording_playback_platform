"""Focused tests for security hardening paths."""
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select


def test_arex_proxy_rejects_invalid_agent_secret(client, monkeypatch):
    import api.arex_proxy as arex_proxy

    monkeypatch.setattr(arex_proxy.settings, "arex_agent_shared_secret", "expected", raising=False)
    monkeypatch.setattr(arex_proxy.settings, "arex_proxy_allow_private_only", True, raising=False)
    monkeypatch.setattr(arex_proxy, "_client_host", lambda request: "192.168.56.10")

    resp = client.post(
        "/api/storage/record/save",
        data=b'{"recordId":"r1","appId":"demo"}',
        headers={"x-arex-agent-secret": "wrong"},
    )

    assert resp.status_code == 401


def test_arex_proxy_accepts_valid_agent_secret(client, monkeypatch):
    import api.arex_proxy as arex_proxy

    monkeypatch.setattr(arex_proxy.settings, "arex_agent_shared_secret", "expected", raising=False)
    monkeypatch.setattr(arex_proxy.settings, "arex_proxy_allow_private_only", True, raising=False)
    monkeypatch.setattr(arex_proxy, "_client_host", lambda request: "192.168.56.10")

    resp = client.post(
        "/api/storage/record/save",
        data=b'{"recordId":"r1","appId":"demo","categoryType":{"name":"Servlet","entryPoint":true}}',
        headers={"x-arex-agent-secret": "expected"},
    )

    assert resp.status_code == 200


def test_arex_proxy_treats_backend_service_url_as_local(monkeypatch):
    import api.arex_proxy as arex_proxy

    monkeypatch.setattr(arex_proxy.settings, "arex_storage_url", "http://backend:8000", raising=False)

    assert arex_proxy._is_proxy_mode() is False


@pytest.mark.asyncio
async def test_cleanup_expired_refresh_tokens(client):
    import database
    from main import _cleanup_expired_refresh_tokens
    from models.auth import RefreshToken
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    async with database.async_session_factory() as db:
        expired = RefreshToken(
            jti="expired",
            username="admin",
            token_hash="old",
            expires_at=now - timedelta(days=10),
        )
        active = RefreshToken(
            jti="active",
            username="admin",
            token_hash="new",
            expires_at=now + timedelta(days=10),
        )
        db.add_all([expired, active])
        await db.commit()

    await _cleanup_expired_refresh_tokens(retention_days=7)

    async with database.async_session_factory() as db:
        remaining = (await db.execute(select(RefreshToken))).scalars().all()

    assert [row.jti for row in remaining] == ["active"]
