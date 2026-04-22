"""Tests for CI token management, trigger replay, and poll result."""
import pytest


def _create_token(client, admin_headers, name="ci-token", expires_days=None):
    payload = {"name": name, "scope": "trigger"}
    if expires_days is not None:
        payload["expires_days"] = expires_days
    resp = client.post("/api/v1/ci/tokens", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_suite_with_case(client, admin_headers):
    """Create an application, a test case, a suite, add the case to the suite."""
    app = client.post(
        "/api/v1/applications",
        json={
            "name": "ci-app",
            "ssh_host": "127.0.0.1",
            "ssh_user": "deploy",
            "ssh_port": 22,
            "service_port": 8080,
        },
        headers=admin_headers,
    ).json()

    tc = client.post(
        "/api/v1/test-cases",
        json={
            "name": "ci-tc",
            "application_id": app["id"],
            "governance_status": "approved",
            "scene_key": "ci-tc|scene",
            "request_method": "GET",
            "request_uri": "/ci-test",
        },
        headers=admin_headers,
    ).json()

    suite = client.post(
        "/api/v1/suites",
        json={"name": "ci-suite"},
        headers=admin_headers,
    ).json()

    add_resp = client.post(
        f"/api/v1/test-cases/{tc['id']}/add-to-suite",
        json={"suite_id": suite["id"]},
        headers=admin_headers,
    )
    assert add_resp.status_code == 201, add_resp.text
    return suite["id"]


def test_create_ci_token(client, admin_headers):
    token_data = _create_token(client, admin_headers)
    assert "plain_token" in token_data
    assert token_data["plain_token"] is not None
    assert token_data["is_active"] is True
    assert token_data["scope"] == "trigger"


def test_create_ci_token_with_expiry(client, admin_headers):
    token_data = _create_token(client, admin_headers, name="expiring-token", expires_days=30)
    assert token_data["expires_at"] is not None


def test_list_ci_tokens(client, admin_headers):
    _create_token(client, admin_headers, name="token-a")
    _create_token(client, admin_headers, name="token-b")
    resp = client.get("/api/v1/ci/tokens", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_revoke_ci_token(client, admin_headers):
    token_data = _create_token(client, admin_headers, name="to-revoke")
    token_id = token_data["id"]

    resp = client.delete(f"/api/v1/ci/tokens/{token_id}", headers=admin_headers)
    assert resp.status_code == 204


def test_ci_token_requires_admin(client, editor_headers):
    resp = client.get("/api/v1/ci/tokens", headers=editor_headers)
    assert resp.status_code == 403


def test_trigger_replay_with_ci_token(client, admin_headers):
    token_data = _create_token(client, admin_headers)
    plain_token = token_data["plain_token"]
    suite_id = _create_suite_with_case(client, admin_headers)

    resp = client.post(
        "/api/v1/ci/trigger",
        json={"suite_id": suite_id},
        headers={"Authorization": f"Token {plain_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "job_id" in body
    assert body["status"] == "PENDING"
    assert body["total"] >= 1


def test_trigger_replay_missing_token(client):
    resp = client.post("/api/v1/ci/trigger", json={"suite_id": 99999})
    assert resp.status_code == 401


def test_trigger_replay_invalid_token(client):
    resp = client.post(
        "/api/v1/ci/trigger",
        json={"suite_id": 99999},
        headers={"Authorization": "Token invalid_token_here"},
    )
    assert resp.status_code == 401


def test_trigger_replay_empty_suite(client, admin_headers):
    token_data = _create_token(client, admin_headers)
    plain_token = token_data["plain_token"]

    suite = client.post(
        "/api/v1/suites",
        json={"name": "empty-suite"},
        headers=admin_headers,
    ).json()

    resp = client.post(
        "/api/v1/ci/trigger",
        json={"suite_id": suite["id"]},
        headers={"Authorization": f"Token {plain_token}"},
    )
    assert resp.status_code == 400


def test_poll_result_with_ci_token(client, admin_headers):
    token_data = _create_token(client, admin_headers)
    plain_token = token_data["plain_token"]
    suite_id = _create_suite_with_case(client, admin_headers)

    trigger_resp = client.post(
        "/api/v1/ci/trigger",
        json={"suite_id": suite_id},
        headers={"Authorization": f"Token {plain_token}"},
    )
    job_id = trigger_resp.json()["job_id"]

    resp = client.get(
        f"/api/v1/ci/result/{job_id}",
        headers={"Authorization": f"Token {plain_token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["job_id"] == job_id
    assert "status" in body
    assert "total" in body
    assert "passed" in body
