"""Tests for replay job creation, execution, result query, and report rendering."""
import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from core.replay_executor import _execute_single, run_replay_job
import database
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase as CaseModel


@pytest.fixture
def tc_payload():
    return {
        "name": "GET /healthz",
        "request_method": "GET",
        "request_uri": "/healthz",
        "expected_status": 200,
    }


def _create_test_case(client, headers, payload):
    resp = client.post("/api/v1/test-cases", json=payload, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_replay_job(client, headers, case_ids, **extra):
    payload = {
        "name": "Test Replay",
        "case_ids": case_ids,
        "concurrency": 1,
        "timeout_ms": 3000,
    }
    payload.update(extra)
    return client.post("/api/v1/replays", json=payload, headers=headers)


def test_create_replay_job(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
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


def test_list_replay_jobs(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    _create_replay_job(client, admin_headers, [tc["id"]])

    resp = client.get("/api/v1/replays", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_get_replay_job(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == job["id"]


def test_get_replay_job_not_found(client, admin_headers):
    resp = client.get("/api/v1/replays/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_list_replay_results(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}/results", headers=admin_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["status"] == "PENDING"


@pytest.mark.asyncio
async def test_execute_single_updates_placeholder_instead_of_inserting_duplicate(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    async with database.async_session_factory() as db:
        case_result = await db.execute(select(CaseModel).where(CaseModel.id == tc["id"]))
        case = case_result.scalar_one()

    class DummyResponse:
        status_code = 200
        text = '{"ok": true}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await _execute_single(
            job_id=job["id"],
            case_id=tc["id"],
            case=case,
            target_host="http://example.com",
            arex_storage_url="http://localhost:8093",
            timeout_ms=1000,
            diff_rules=None,
            assertions_config=None,
            perf_threshold_ms=None,
            use_mocks=False,
        )

    async with database.async_session_factory() as db:
        results = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]).order_by(ReplayResult.id))
        ).scalars().all()
    assert len(results) == 1
    assert results[0].status in {"PASS", "FAIL"}


def test_html_report(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}/report", headers=admin_headers)
    assert resp.status_code == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert "\u56de\u653e\u62a5\u544a" in resp.text


def test_replay_job_fields(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
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


@pytest.mark.asyncio
async def test_run_replay_job_marks_job_failed_when_any_case_fails(client, admin_headers, created_app):
    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "diff-case",
            "application_id": created_app["id"],
            "request_method": "GET",
            "request_uri": "/healthz",
            "expected_response": '{"expected": true}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job = _create_replay_job(client, admin_headers, [tc["id"]], application_id=created_app["id"]).json()

    class DummyResponse:
        status_code = 200
        text = '{"actual": true}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        job_row = (
            await db.execute(select(ReplayJob).where(ReplayJob.id == job["id"]))
        ).scalar_one()
    assert job_row.status == "FAILED"
