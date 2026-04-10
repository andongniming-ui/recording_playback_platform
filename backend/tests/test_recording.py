"""Tests for recording session CRUD, recording listing, and session sync."""
import pytest
from unittest.mock import AsyncMock, patch

import database
from sqlalchemy import select
from api.v1.sessions import _sync_from_arex_storage
from models.recording import Recording


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

def _create_session(client, app_id, headers, name="test-session"):
    return client.post(
        "/api/v1/sessions",
        json={"application_id": app_id, "name": name},
        headers=headers,
    )


def test_create_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = _create_session(client, app_id, admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "test-session"
    assert body["status"] == "idle"
    assert body["application_id"] == app_id


def test_list_sessions(client, admin_headers, created_app):
    app_id = created_app["id"]
    _create_session(client, app_id, admin_headers, "sess-a")
    _create_session(client, app_id, admin_headers, "sess-b")

    resp = client.get("/api/v1/sessions", headers=admin_headers)
    assert resp.status_code == 200
    sessions = resp.json()
    assert len(sessions) >= 2


def test_list_sessions_filter_by_app(client, admin_headers, created_app):
    app_id = created_app["id"]
    _create_session(client, app_id, admin_headers, "filtered-session")

    resp = client.get(
        f"/api/v1/sessions?application_id={app_id}", headers=admin_headers
    )
    assert resp.status_code == 200
    for s in resp.json():
        assert s["application_id"] == app_id


def test_get_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    created = _create_session(client, app_id, admin_headers).json()
    sess_id = created["id"]

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sess_id


def test_get_session_not_found(client, admin_headers):
    resp = client.get("/api/v1/sessions/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_delete_session(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    resp = client.delete(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 204

    resp2 = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp2.status_code == 404


def test_create_session_invalid_app(client, admin_headers):
    resp = client.post(
        "/api/v1/sessions",
        json={"application_id": 9999, "name": "orphan"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Recording listing
# ---------------------------------------------------------------------------

def test_list_recordings_empty(client, admin_headers, created_app):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    resp = client.get(f"/api/v1/sessions/{sess_id}/recordings", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_sync_session_keeps_total_count_as_session_total_and_parses_operation_name(
    client, admin_headers, created_app
):
    app_id = created_app["id"]
    sess_id = _create_session(client, app_id, admin_headers).json()["id"]

    query_side_effect = [
        {"body": [{"recordId": "r-1"}, {"recordId": "r-2"}]},
        {"body": [{"recordId": "r-2"}, {"recordId": "r-3"}]},
    ]

    async def fake_view_recording(*args):
        record_id = args[-1]
        return {
            "operationName": {
                "r-1": "GET /api/orders/1",
                "r-2": "POST /api/orders",
                "r-3": "DELETE /api/orders/3",
            }[record_id],
            "requestHeaders": {"Content-Type": "application/json"},
            "targetRequest": "<xml><id>r-3</id></xml>" if record_id == "r-3" else {"id": record_id},
            "responseStatusCode": 200,
            "targetResponse": "<xml><ok>true</ok></xml>" if record_id == "r-3" else {"ok": True},
        }

    with (
        patch("api.v1.sessions.async_session_factory", database.async_session_factory),
        patch("integration.arex_client.ArexClient.query_recordings", new=AsyncMock(side_effect=query_side_effect)),
        patch("integration.arex_client.ArexClient.view_recording", new=AsyncMock(side_effect=fake_view_recording)),
    ):
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )
        await _sync_from_arex_storage(
            session_id=sess_id,
            application_id=app_id,
            begin_time=None,
            end_time=None,
            page_size=50,
            page_index=0,
        )

    resp = client.get(f"/api/v1/sessions/{sess_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total_count"] == 3

    async with database.async_session_factory() as db:
        rows = (
            await db.execute(
                select(Recording).where(Recording.session_id == sess_id).order_by(Recording.record_id)
            )
        ).scalars().all()

    assert [row.record_id for row in rows] == ["r-1", "r-2", "r-3"]
    assert rows[0].request_method == "GET"
    assert rows[0].request_uri == "/api/orders/1"
    assert rows[1].request_method == "POST"
    assert rows[1].request_uri == "/api/orders"
    assert rows[2].request_body == "<xml><id>r-3</id></xml>"
    assert rows[2].response_body == "<xml><ok>true</ok></xml>"
