"""Tests for recording session CRUD, recording listing, and session sync."""
import pytest


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
