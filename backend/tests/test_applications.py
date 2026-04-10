"""Tests for application CRUD, test-connection (mocked SSH), and mount-agent."""
import pytest
from unittest.mock import patch


APP_PAYLOAD = {
    "name": "my-service",
    "ssh_host": "10.0.0.5",
    "ssh_user": "ubuntu",
    "ssh_port": 22,
    "service_port": 8080,
}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def test_create_application(client, admin_headers):
    resp = client.post("/api/v1/applications", json=APP_PAYLOAD, headers=admin_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "my-service"
    assert body["agent_status"] in ("unknown", "offline")
    assert "id" in body


def test_list_applications(client, admin_headers):
    client.post("/api/v1/applications", json=APP_PAYLOAD, headers=admin_headers)
    resp = client.get("/api/v1/applications", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == app_id


def test_get_application_not_found(client, admin_headers):
    resp = client.get("/api/v1/applications/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.put(
        f"/api/v1/applications/{app_id}",
        json={"description": "updated description"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated description"


def test_delete_application(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.delete(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp.status_code == 204

    # Should now return 404
    resp2 = client.get(f"/api/v1/applications/{app_id}", headers=admin_headers)
    assert resp2.status_code == 404


def test_create_application_requires_auth(client):
    resp = client.post("/api/v1/applications", json=APP_PAYLOAD)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# SSH / Agent endpoints (mocked)
# ---------------------------------------------------------------------------

def test_test_connection_success(client, admin_headers, created_app):
    app_id = created_app["id"]
    mock_result = {"success": True, "latency_ms": 5}
    with patch(
        "integration.ssh_executor.test_connection",
        return_value=mock_result,
    ):
        resp = client.post(
            f"/api/v1/applications/{app_id}/test-connection",
            headers=admin_headers,
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_mount_agent_starts_background(client, admin_headers, created_app):
    app_id = created_app["id"]
    resp = client.post(
        f"/api/v1/applications/{app_id}/mount-agent",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "mounting"
