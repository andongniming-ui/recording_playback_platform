"""Tests for schedule CRUD and trigger endpoint (with mocked scheduler)."""
import pytest
from unittest.mock import patch, AsyncMock


def _create_suite(client, headers, name="nightly-suite"):
    resp = client.post("/api/v1/suites", json={"name": name}, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_case(client, headers, app_id, name="nightly-case", uri="/api/nightly"):
    resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": name,
            "application_id": app_id,
            "request_method": "GET",
            "request_uri": uri,
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def _bind_suite_cases(client, headers, suite_id, case_ids):
    resp = client.put(f"/api/v1/suites/{suite_id}/cases", json={"case_ids": case_ids}, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


@pytest.fixture
def schedule_payload():
    """Return a fresh schedule payload dict for each test."""
    return {
        "name": "nightly-run",
        "cron_expr": "0 2 * * *",
        "is_active": True,
        "notify_type": "none",
    }


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def test_create_schedule(client, admin_headers, schedule_payload):
    resp = client.post(
        "/api/v1/schedules", json=schedule_payload, headers=admin_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "nightly-run"
    assert body["cron_expr"] == "0 2 * * *"
    assert "id" in body


def test_list_schedules(client, admin_headers, schedule_payload):
    client.post("/api/v1/schedules", json=schedule_payload, headers=admin_headers)
    resp = client.get("/api/v1/schedules", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) == 1


def test_get_schedule(client, admin_headers, schedule_payload):
    sched = client.post(
        "/api/v1/schedules", json=schedule_payload, headers=admin_headers
    ).json()
    resp = client.get(f"/api/v1/schedules/{sched['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sched["id"]


def test_get_schedule_not_found(client, admin_headers):
    resp = client.get("/api/v1/schedules/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_schedule(client, admin_headers, schedule_payload):
    sched = client.post(
        "/api/v1/schedules", json=schedule_payload, headers=admin_headers
    ).json()
    resp = client.put(
        f"/api/v1/schedules/{sched['id']}",
        json={"cron_expr": "0 3 * * *"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["cron_expr"] == "0 3 * * *"


def test_delete_schedule(client, admin_headers, schedule_payload):
    sched = client.post(
        "/api/v1/schedules", json=schedule_payload, headers=admin_headers
    ).json()
    resp = client.delete(
        f"/api/v1/schedules/{sched['id']}", headers=admin_headers
    )
    assert resp.status_code == 204

    resp2 = client.get(f"/api/v1/schedules/{sched['id']}", headers=admin_headers)
    assert resp2.status_code == 404


# ---------------------------------------------------------------------------
# Trigger
# ---------------------------------------------------------------------------

def test_trigger_schedule(client, admin_headers, schedule_payload, created_app):
    suite = _create_suite(client, admin_headers)
    case = _create_case(client, admin_headers, created_app["id"])
    _bind_suite_cases(client, admin_headers, suite["id"], [case["id"]])
    sched = client.post(
        "/api/v1/schedules", json={**schedule_payload, "suite_id": suite["id"]}, headers=admin_headers
    ).json()
    resp = client.post(
        f"/api/v1/schedules/{sched['id']}/trigger",
        headers=admin_headers,
    )
    # trigger_now is mocked to AsyncMock in conftest so it should succeed
    assert resp.status_code == 200
    assert "triggered" in resp.json().get("message", "")


def test_trigger_schedule_not_found(client, admin_headers):
    resp = client.post(
        "/api/v1/schedules/9999/trigger",
        headers=admin_headers,
    )
    assert resp.status_code == 404


def test_trigger_schedule_without_suite_returns_400(client, admin_headers, schedule_payload):
    sched = client.post(
        "/api/v1/schedules", json={**schedule_payload, "is_active": False}, headers=admin_headers
    ).json()
    resp = client.post(
        f"/api/v1/schedules/{sched['id']}/trigger",
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert "bound to a suite" in resp.json()["detail"]


def test_trigger_schedule_with_empty_suite_returns_400(client, admin_headers, schedule_payload):
    suite = _create_suite(client, admin_headers, name="empty-suite")
    sched = client.post(
        "/api/v1/schedules",
        json={**schedule_payload, "suite_id": suite["id"], "is_active": False},
        headers=admin_headers,
    ).json()
    resp = client.post(
        f"/api/v1/schedules/{sched['id']}/trigger",
        headers=admin_headers,
    )
    assert resp.status_code == 400
    assert "no test cases" in resp.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_create_schedule_invalid_notify_type(client, admin_headers, schedule_payload):
    payload = dict(schedule_payload, notify_type="slack")
    resp = client.post("/api/v1/schedules", json=payload, headers=admin_headers)
    assert resp.status_code == 422


def test_create_schedule_with_missing_suite_returns_404(client, admin_headers, schedule_payload):
    resp = client.post(
        "/api/v1/schedules",
        json={**schedule_payload, "suite_id": 99999},
        headers=admin_headers,
    )
    assert resp.status_code == 404
