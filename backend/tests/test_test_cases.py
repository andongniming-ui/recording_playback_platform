"""Tests for test case CRUD, clone, export, import, from-recording, add-to-suite."""
import json
import io
import pytest


TC_PAYLOAD = {
    "name": "GET /api/users",
    "request_method": "GET",
    "request_uri": "/api/users",
    "expected_status": 200,
}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def _create_tc(client, headers, **overrides):
    payload = dict(TC_PAYLOAD, **overrides)
    resp = client.post("/api/v1/test-cases", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_create_test_case(client, admin_headers):
    body = _create_tc(client, admin_headers)
    assert body["name"] == TC_PAYLOAD["name"]
    assert body["status"] == "draft"
    assert "id" in body


def test_list_test_cases(client, admin_headers):
    _create_tc(client, admin_headers, name="case-1")
    _create_tc(client, admin_headers, name="case-2")

    resp = client.get("/api/v1/test-cases", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_get_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.get(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == tc["id"]


def test_get_test_case_not_found(client, admin_headers):
    resp = client.get("/api/v1/test-cases/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.put(
        f"/api/v1/test-cases/{tc['id']}",
        json={"status": "active"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_delete_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    resp = client.delete(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp.status_code == 204

    resp2 = client.get(f"/api/v1/test-cases/{tc['id']}", headers=admin_headers)
    assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# Clone
# ---------------------------------------------------------------------------

def test_clone_test_case(client, admin_headers):
    tc = _create_tc(client, admin_headers, name="original")
    resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/clone",
        headers=admin_headers,
    )
    assert resp.status_code == 201
    clone = resp.json()
    assert clone["name"] == "original (copy)"
    assert clone["id"] != tc["id"]
    assert clone["status"] == "draft"


# ---------------------------------------------------------------------------
# Export / Import
# ---------------------------------------------------------------------------

def test_export_test_cases(client, admin_headers):
    tc = _create_tc(client, admin_headers, name="export-me")
    resp = client.get(
        f"/api/v1/test-cases/export?ids={tc['id']}",
        headers=admin_headers,
    )
    assert resp.status_code == 200
    exported = resp.json()
    assert isinstance(exported, list)
    assert exported[0]["name"] == "export-me"


def test_import_test_cases(client, admin_headers):
    cases = [
        {
            "name": "imported-case",
            "request_method": "POST",
            "request_uri": "/api/login",
        }
    ]
    file_bytes = json.dumps(cases).encode()
    resp = client.post(
        "/api/v1/test-cases/import",
        files={"file": ("cases.json", io.BytesIO(file_bytes), "application/json")},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["imported"] == 1


def test_import_invalid_json(client, admin_headers):
    resp = client.post(
        "/api/v1/test-cases/import",
        files={"file": ("bad.json", io.BytesIO(b"not json at all"), "application/json")},
        headers=admin_headers,
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Add to suite
# ---------------------------------------------------------------------------

def test_add_to_suite(client, admin_headers):
    tc = _create_tc(client, admin_headers)
    # Create suite
    suite_resp = client.post(
        "/api/v1/suites",
        json={"name": "my-suite"},
        headers=admin_headers,
    )
    assert suite_resp.status_code == 201
    suite_id = suite_resp.json()["id"]

    resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/add-to-suite",
        json={"suite_id": suite_id},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["order_index"] == 1
