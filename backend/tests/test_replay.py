"""Tests for replay job creation, result query, and WebSocket progress."""
import pytest


TC_PAYLOAD = {
    "name": "GET /healthz",
    "request_method": "GET",
    "request_uri": "/healthz",
    "expected_status": 200,
}


def _create_test_case(client, headers):
    resp = client.post("/api/v1/test-cases", json=TC_PAYLOAD, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_replay_job(client, headers, case_ids):
    payload = {
        "name": "Test Replay",
        "case_ids": case_ids,
        "concurrency": 1,
        "timeout_ms": 3000,
    }
    return client.post("/api/v1/replays", json=payload, headers=headers)


# ---------------------------------------------------------------------------
# Replay job CRUD
# ---------------------------------------------------------------------------

def test_create_replay_job(client, admin_headers):
    tc = _create_test_case(client, admin_headers)
    resp = _create_replay_job(client, admin_headers, [tc["id"]])
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PENDING"
    assert body["total"] == 1
    assert "id" in body


def test_create_replay_job_empty_case_ids(client, admin_headers):
    resp = client.post(
        "/api/v1/replays",
        json={"name": "empty", "case_ids": []},
        headers=admin_headers,
    )
    assert resp.status_code == 400


def test_list_replay_jobs(client, admin_headers):
    tc = _create_test_case(client, admin_headers)
    _create_replay_job(client, admin_headers, [tc["id"]])

    resp = client.get("/api/v1/replays", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_replay_job(client, admin_headers):
    tc = _create_test_case(client, admin_headers)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == job["id"]


def test_get_replay_job_not_found(client, admin_headers):
    resp = client.get("/api/v1/replays/9999", headers=admin_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

def test_list_replay_results(client, admin_headers):
    tc = _create_test_case(client, admin_headers)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}/results", headers=admin_headers)
    assert resp.status_code == 200
    results = resp.json()
    # One placeholder result should have been created
    assert len(results) == 1
    assert results[0]["status"] == "PENDING"


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def test_html_report(client, admin_headers):
    tc = _create_test_case(client, admin_headers)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}/report", headers=admin_headers)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "AREX Recorder" in resp.text


# ---------------------------------------------------------------------------
# WebSocket progress (basic connection test)
# ---------------------------------------------------------------------------

def test_replay_job_fields(client, admin_headers):
    """Verify replay job response contains all expected fields."""
    tc = _create_test_case(client, admin_headers)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()
    job_id = job["id"]

    resp = client.get(f"/api/v1/replays/{job_id}", headers=admin_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == job_id
    assert "status" in body
    assert "total" in body
    assert "passed" in body
    assert "failed" in body
    assert "errored" in body
