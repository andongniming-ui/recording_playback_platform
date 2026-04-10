"""Tests for schedule CRUD and trigger endpoint (with mocked scheduler)."""
import pytest
from unittest.mock import patch, AsyncMock


SCHEDULE_PAYLOAD = {
    "name": "nightly-run",
    "cron_expr": "0 2 * * *",
    "is_active": True,
    "notify_type": "none",
}


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def test_create_schedule(client, admin_headers):
    resp = client.post(
        "/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "nightly-run"
    assert body["cron_expr"] == "0 2 * * *"
    assert "id" in body


def test_list_schedules(client, admin_headers):
    client.post("/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers)
    resp = client.get("/api/v1/schedules", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_schedule(client, admin_headers):
    sched = client.post(
        "/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers
    ).json()
    resp = client.get(f"/api/v1/schedules/{sched['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == sched["id"]


def test_get_schedule_not_found(client, admin_headers):
    resp = client.get("/api/v1/schedules/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_update_schedule(client, admin_headers):
    sched = client.post(
        "/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers
    ).json()
    resp = client.put(
        f"/api/v1/schedules/{sched['id']}",
        json={"cron_expr": "0 3 * * *"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["cron_expr"] == "0 3 * * *"


def test_delete_schedule(client, admin_headers):
    sched = client.post(
        "/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers
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

def test_trigger_schedule(client, admin_headers):
    sched = client.post(
        "/api/v1/schedules", json=SCHEDULE_PAYLOAD, headers=admin_headers
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


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def test_create_schedule_invalid_notify_type(client, admin_headers):
    payload = dict(SCHEDULE_PAYLOAD, notify_type="slack")
    resp = client.post("/api/v1/schedules", json=payload, headers=admin_headers)
    assert resp.status_code == 422
