"""Tests for replay job creation, execution, result query, and report rendering."""
import asyncio
import json
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import select, update

from api.v1.replays import _build_result_source_context, _count_sub_call_nodes
from api.v1.replays import get_html_report, get_replay_result, list_results
from core.replay_executor import _execute_single, run_replay_job
import database
from models.audit import ReplayAuditLog
from models.recording import Recording
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


def test_create_replay_job_allows_target_application_different_from_test_case_application(
    client, admin_headers, tc_payload, app_payload
):
    source_app_resp = client.post("/api/v1/applications", json=app_payload, headers=admin_headers)
    assert source_app_resp.status_code == 201, source_app_resp.text
    source_app = source_app_resp.json()

    target_payload = dict(app_payload)
    target_payload["name"] = "target-app"
    target_payload["service_port"] = 8081
    target_app_resp = client.post("/api/v1/applications", json=target_payload, headers=admin_headers)
    assert target_app_resp.status_code == 201, target_app_resp.text
    target_app = target_app_resp.json()

    tc = _create_test_case(
        client,
        admin_headers,
        {
            **tc_payload,
            "application_id": source_app["id"],
        },
    )
    resp = _create_replay_job(
        client,
        admin_headers,
        [tc["id"]],
        application_id=target_app["id"],
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["application_id"] == target_app["id"]


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


def test_list_replay_jobs_supports_search_and_status_filters(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    created = _create_replay_job(client, admin_headers, [tc["id"]], name="nightly-health-check").json()

    resp = client.get(
        "/api/v1/replays",
        params={"search": "nightly", "status": "PENDING"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]
    assert body[0]["name"] == "nightly-health-check"


def test_list_replay_jobs_supports_created_at_sort_order(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    first = _create_replay_job(client, admin_headers, [tc["id"]], name="sort-job-1").json()
    second = _create_replay_job(client, admin_headers, [tc["id"]], name="sort-job-2").json()

    async def _seed_order():
        async with database.async_session_factory() as db:
            await db.execute(
                update(ReplayJob)
                .where(ReplayJob.id == first["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T09:00:00"))
            )
            await db.execute(
                update(ReplayJob)
                .where(ReplayJob.id == second["id"])
                .values(created_at=datetime.fromisoformat("2026-04-21T10:00:00"))
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_seed_order())

    asc_resp = client.get(
        "/api/v1/replays",
        params={"sort_by": "created_at", "sort_order": "asc"},
        headers=admin_headers,
    )
    assert asc_resp.status_code == 200
    asc_ids = [item["id"] for item in asc_resp.json()[:2]]
    assert asc_ids == [first["id"], second["id"]]

    desc_resp = client.get(
        "/api/v1/replays",
        params={"sort_by": "created_at", "sort_order": "desc"},
        headers=admin_headers,
    )
    assert desc_resp.status_code == 200
    desc_ids = [item["id"] for item in desc_resp.json()[:2]]
    assert desc_ids == [second["id"], first["id"]]


def test_get_replay_job(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == job["id"]


def test_get_replay_job_not_found(client, admin_headers):
    resp = client.get("/api/v1/replays/9999", headers=admin_headers)
    assert resp.status_code == 404


def test_replay_result_rule_suggestions_can_apply_ignore_fields(client, admin_headers, app_payload):
    app_resp = client.post("/api/v1/applications", json=app_payload, headers=admin_headers)
    assert app_resp.status_code == 201, app_resp.text
    app = app_resp.json()

    tc = _create_test_case(
        client,
        admin_headers,
        {
            "name": "POST /orders",
            "application_id": app["id"],
            "request_method": "POST",
            "request_uri": "/orders",
            "expected_status": 200,
        },
    )
    job = _create_replay_job(client, admin_headers, [tc["id"]], application_id=app["id"]).json()

    async def _seed_result():
        async with database.async_session_factory() as db:
            row = await db.execute(
                select(ReplayResult).where(
                    ReplayResult.job_id == job["id"],
                    ReplayResult.test_case_id == tc["id"],
                )
            )
            rr = row.scalar_one()
            rr.status = "FAIL"
            rr.request_method = "POST"
            rr.request_uri = "/orders"
            rr.actual_status_code = 200
            rr.expected_response = '{"data":{"timestamp":"old"}}'
            rr.actual_response = '{"data":{"timestamp":"new"}}'
            rr.diff_result = json.dumps(
                {
                    "values_changed": {
                        "root['data']['timestamp']": {
                            "old_value": "old",
                            "new_value": "new",
                        }
                    }
                }
            )
            rr.diff_score = 0.5
            rr.is_pass = False
            await db.commit()
            await db.refresh(rr)
            return rr.id

    result_id = asyncio.get_event_loop().run_until_complete(_seed_result())

    suggestions = client.get(
        f"/api/v1/replays/results/{result_id}/rule-suggestions",
        headers=admin_headers,
    )
    assert suggestions.status_code == 200, suggestions.text
    body = suggestions.json()
    assert body["suggestions"][0]["field"] == "timestamp"
    assert body["suggestions"][0]["path"] == "data.timestamp"

    applied = client.post(
        f"/api/v1/replays/results/{result_id}/rule-suggestions/apply",
        json={"suggestion_key": "timestamp", "target": "application_default_ignore_fields"},
        headers=admin_headers,
    )
    assert applied.status_code == 200, applied.text
    assert applied.json()["ignore_fields"] == ["timestamp"]

    fetched_app = client.get(f"/api/v1/applications/{app['id']}", headers=admin_headers)
    assert fetched_app.status_code == 200
    assert fetched_app.json()["default_ignore_fields"] == ["timestamp"]


def test_delete_replay_job_removes_results(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.delete(f"/api/v1/replays/{job['id']}", headers=admin_headers)
    assert resp.status_code == 204

    missing = client.get(f"/api/v1/replays/{job['id']}", headers=admin_headers)
    assert missing.status_code == 404

    async def _count_results():
        async with database.async_session_factory() as db:
            return (
                await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
            ).scalars().all()

    assert asyncio.get_event_loop().run_until_complete(_count_results()) == []


def test_bulk_delete_replay_jobs_blocks_running_and_deletes_pending(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    deletable = _create_replay_job(client, admin_headers, [tc["id"]], name="deletable-job").json()
    running = _create_replay_job(client, admin_headers, [tc["id"]], name="running-job").json()

    async def _mark_running():
        async with database.async_session_factory() as db:
            await db.execute(
                update(ReplayJob)
                .where(ReplayJob.id == running["id"])
                .values(status="RUNNING")
            )
            await db.commit()

    asyncio.get_event_loop().run_until_complete(_mark_running())

    blocked = client.post(
        "/api/v1/replays/bulk-delete",
        json={"ids": [deletable["id"], running["id"]]},
        headers=admin_headers,
    )
    assert blocked.status_code == 409

    deleted = client.post(
        "/api/v1/replays/bulk-delete",
        json={"ids": [deletable["id"]]},
        headers=admin_headers,
    )
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] == 1

    missing = client.get(f"/api/v1/replays/{deletable['id']}", headers=admin_headers)
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_startup_recovery_fails_stale_running_job_and_pending_results(client, admin_headers, tc_payload):
    from main import _recover_stale_running_jobs
    from utils.timezone import now_beijing

    first = _create_test_case(client, admin_headers, {**tc_payload, "name": "first"})
    second = _create_test_case(client, admin_headers, {**tc_payload, "name": "second"})
    job = _create_replay_job(client, admin_headers, [first["id"], second["id"]]).json()

    old_heartbeat = now_beijing() - timedelta(minutes=10)
    async with database.async_session_factory() as db:
        await db.execute(
            update(ReplayJob)
            .where(ReplayJob.id == job["id"])
            .values(
                status="RUNNING",
                total=2,
                passed=0,
                failed=0,
                errored=0,
                started_at=old_heartbeat,
                heartbeat_at=old_heartbeat,
                worker_id="old-worker",
            )
        )
        await db.execute(
            update(ReplayResult)
            .where(ReplayResult.job_id == job["id"], ReplayResult.test_case_id == first["id"])
            .values(status="PASS", is_pass=True)
        )
        await db.commit()

    recovered = await _recover_stale_running_jobs(stale_after=timedelta(seconds=1))
    assert recovered == 1

    async with database.async_session_factory() as db:
        fetched_job = (
            await db.execute(select(ReplayJob).where(ReplayJob.id == job["id"]))
        ).scalar_one()
        results = (
            await db.execute(
                select(ReplayResult)
                .where(ReplayResult.job_id == job["id"])
                .order_by(ReplayResult.test_case_id)
            )
        ).scalars().all()
        audit = (
            await db.execute(
                select(ReplayAuditLog).where(
                    ReplayAuditLog.job_id == job["id"],
                    ReplayAuditLog.event_type == "job_recovered_failed",
                )
            )
        ).scalar_one_or_none()

    assert fetched_job.status == "FAILED"
    assert fetched_job.passed == 1
    assert fetched_job.failed == 0
    assert fetched_job.errored == 1
    assert fetched_job.finished_at is not None
    assert fetched_job.worker_id is None
    assert [result.status for result in results] == ["PASS", "ERROR"]
    assert results[1].failure_category == "job_interrupted"
    assert audit is not None


@pytest.mark.asyncio
async def test_startup_recovery_keeps_fresh_running_job(client, admin_headers, tc_payload):
    from main import _recover_stale_running_jobs
    from utils.timezone import now_beijing

    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    async with database.async_session_factory() as db:
        await db.execute(
            update(ReplayJob)
            .where(ReplayJob.id == job["id"])
            .values(status="RUNNING", heartbeat_at=now_beijing(), worker_id="active-worker")
        )
        await db.commit()

    recovered = await _recover_stale_running_jobs(stale_after=timedelta(minutes=10))
    assert recovered == 0

    async with database.async_session_factory() as db:
        fetched_job = (
            await db.execute(select(ReplayJob).where(ReplayJob.id == job["id"]))
        ).scalar_one()
        result = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()

    assert fetched_job.status == "RUNNING"
    assert fetched_job.worker_id == "active-worker"
    assert result.status == "PENDING"


def test_list_replay_results(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    resp = client.get(f"/api/v1/replays/{job['id']}/results", headers=admin_headers)
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["status"] == "PENDING"


@pytest.mark.asyncio
async def test_replay_audit_logs_capture_execution_flow(client, admin_headers, tc_payload, created_app):
    tc = _create_test_case(
        client,
        admin_headers,
        {
            **tc_payload,
            "application_id": created_app["id"],
        },
    )
    job = _create_replay_job(client, admin_headers, [tc["id"]]).json()

    class DummyResponse:
        status_code = 200
        text = '{"ok": true}'
        headers = {}

    with patch("httpx.AsyncClient.request", AsyncMock(return_value=DummyResponse())):
        await run_replay_job(job["id"])

    resp = client.get(f"/api/v1/replays/{job['id']}/audit-logs", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    event_types = {item["event_type"] for item in body}
    assert {"job_started", "case_started", "request_sent", "response_received", "case_finished", "job_finished"} <= event_types
    assert any(
        item["event_type"] == "case_finished"
        and item["detail"]
        and json.loads(item["detail"]).get("status") in {"PASS", "FAIL", "ERROR", "TIMEOUT"}
        for item in body
    )
    case_finished_entry = next(item for item in body if item["event_type"] == "case_finished")

    filtered_resp = client.get(
        f"/api/v1/replays/{job['id']}/audit-logs",
        params={
            "event_type": "case_finished",
            "case_id": tc["id"],
            "result_id": case_finished_entry["result_id"],
        },
        headers=admin_headers,
    )
    assert filtered_resp.status_code == 200, filtered_resp.text
    filtered_body = filtered_resp.json()
    assert len(filtered_body) == 1
    assert filtered_body[0]["test_case_id"] == tc["id"]

    async with database.async_session_factory() as db:
        result = await db.execute(select(ReplayAuditLog).where(ReplayAuditLog.job_id == job["id"]))
        assert len(result.scalars().all()) >= 6


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
    assert "回放测试报告" in resp.text


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


def test_create_replay_job_persists_advanced_config(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client,
        admin_headers,
        [tc["id"]],
        delay_ms=250,
        ignore_fields=["timestamp", "traceId"],
        use_sub_invocation_mocks=True,
        diff_rules=[{"type": "ignore", "path": "timestamp"}],
        assertions=[{"type": "status_code_eq", "value": 200}],
        perf_threshold_ms=1200,
        smart_noise_reduction=True,
        retry_count=2,
        header_transforms=[{"type": "replace", "key": "X-Test", "value": "1"}],
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["delay_ms"] == 250
    assert body["ignore_fields"] == ["timestamp", "traceId"]
    assert body["use_sub_invocation_mocks"] is True
    assert body["smart_noise_reduction"] is True
    assert body["retry_count"] == 2
    assert body["header_transforms"] == [{"type": "replace", "key": "X-Test", "value": "1"}]
    assert len(body["diff_rules"]) == 1
    assert body["diff_rules"][0]["type"] == "ignore"
    assert body["diff_rules"][0]["path"] == "timestamp"
    assert len(body["assertions"]) == 1
    assert body["assertions"][0]["type"] == "status_code_eq"
    assert body["assertions"][0]["value"] == 200


def test_count_sub_call_nodes_counts_nested_children():
    payload = [
        {
            "type": "MySQL",
            "children": [
                {"type": "Redis"},
                {"type": "RPC", "children": [{"type": "HTTP"}]},
            ],
        }
    ]
    assert _count_sub_call_nodes(payload) == 4


@pytest.mark.asyncio
async def test_build_result_source_context_includes_mock_and_source_recording_fields():
    replay_result = SimpleNamespace(job_id=11, test_case_id=22)
    job = SimpleNamespace(use_sub_invocation_mocks=True)
    test_case = SimpleNamespace(source_recording_id=33)
    recording = SimpleNamespace(
        transaction_code="OPEN_ACCOUNT",
        scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
        sub_calls=json.dumps([
            {"type": "MySQL"},
            {"type": "Redis", "children": [{"type": "RPC"}]},
        ], ensure_ascii=False),
    )

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[
        DummyResult(job),
        DummyResult(test_case),
        DummyResult(recording),
    ])

    context = await _build_result_source_context(db, replay_result)
    assert context["use_sub_invocation_mocks"] is True
    assert context["source_recording_id"] == 33
    assert context["source_recording_transaction_code"] == "OPEN_ACCOUNT"
    assert context["source_recording_scene_key"] == "OPEN_ACCOUNT|POST|/api/bank/service|success"
    assert context["source_recording_sub_call_count"] == 3


@pytest.mark.asyncio
async def test_execute_single_loads_and_removes_mock_when_enabled():
    case = SimpleNamespace(
        id=1,
        source_recording_id=2,
        request_method="POST",
        request_uri="/api/bank/service",
        request_headers=None,
        request_body='{"service_id":"OPEN_ACCOUNT"}',
        expected_response='{"code": 0}',
        expected_status=200,
        ignore_fields=None,
        assert_rules=None,
    )
    recording = SimpleNamespace(record_id="mock-record-1", sub_calls=None)

    class DummyResponse:
        status_code = 200
        text = '{"code": 0}'

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    class DummySession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def execute(self, *args, **kwargs):
            return DummyResult(recording)

    load_mock = AsyncMock(return_value={"ok": True})
    remove_mock = AsyncMock(return_value={"ok": True})
    save_mock = AsyncMock(return_value=SimpleNamespace(status="PASS"))

    with (
        patch("database.async_session_factory", lambda: DummySession()),
        patch("httpx.AsyncClient.request", AsyncMock(return_value=DummyResponse())),
        patch("integration.arex_client.ArexClient.cache_load_mock", load_mock),
        patch("integration.arex_client.ArexClient.cache_remove_mock", remove_mock),
        patch("core.replay_executor._save_result", save_mock),
    ):
        result = await _execute_single(
            job_id=11,
            case_id=1,
            case=case,
            target_host="http://example.com",
            arex_storage_url="http://localhost:8093",
            timeout_ms=1000,
            diff_rules=None,
            assertions_config=None,
            perf_threshold_ms=None,
            use_mocks=True,
        )

    load_mock.assert_awaited_once_with("mock-record-1")
    remove_mock.assert_awaited_once_with("mock-record-1")
    assert result.status == "PASS"


@pytest.mark.asyncio
async def test_execute_single_applies_transaction_mappings_for_request_and_response():
    case = SimpleNamespace(
        id=2,
        source_recording_id=None,
        transaction_code="car001_open",
        request_method="POST",
        request_uri="/api/bank/service",
        request_headers=None,
        request_body="""
            <request>
              <name>张三</name>
              <branch_code></branch_code>
              <debug_flag>1</debug_flag>
            </request>
        """.strip(),
        expected_response="<response><name>张三</name></response>",
        expected_status=200,
        ignore_fields=None,
        assert_rules=None,
    )
    transaction_mappings = [
        {
            "transaction_code": "car001_open",
            "enabled": True,
            "request_rules": [
                {"type": "rename", "source": "name", "target": "cst_name"},
                {"type": "default", "source": "branch_code", "value": "0101"},
                {"type": "delete", "source": "debug_flag"},
            ],
            "response_rules": [
                {"type": "rename", "source": "cst_name", "target": "name"},
                {"type": "delete", "source": "debug_flag"},
            ],
        }
    ]

    captured = {}

    class DummyResponse:
        status_code = 200
        text = "<response><cst_name>张三</cst_name><debug_flag>1</debug_flag></response>"

    async def fake_request(*args, **kwargs):
        captured["content"] = kwargs.get("content")
        captured["headers"] = kwargs.get("headers")
        return DummyResponse()

    def fake_compute_diff(original, replayed, **kwargs):
        assert original == "<response><name>张三</name></response>"
        assert "<name>张三</name>" in replayed
        assert "<cst_name>" not in replayed
        assert "<debug_flag>" not in replayed
        return None, 0.0

    save_mock = AsyncMock(return_value=SimpleNamespace(status="PASS"))

    with (
        patch("httpx.AsyncClient.request", new=AsyncMock(side_effect=fake_request)),
        patch("core.replay_executor.compute_diff", side_effect=fake_compute_diff),
        patch("core.replay_executor._save_result", save_mock),
    ):
        result = await _execute_single(
            job_id=12,
            case_id=2,
            case=case,
            target_host="http://example.com",
            arex_storage_url="http://localhost:8093",
            timeout_ms=1000,
            diff_rules=None,
            assertions_config=None,
            perf_threshold_ms=None,
            use_mocks=False,
            transaction_mappings=transaction_mappings,
        )

    assert result.status == "PASS"
    sent_body = captured["content"].decode()
    assert "<cst_name>张三</cst_name>" in sent_body
    assert "<branch_code>0101</branch_code>" in sent_body
    assert "<name>张三</name>" not in sent_body
    assert "<debug_flag>" not in sent_body
    saved_kwargs = save_mock.await_args.kwargs
    # Bug 1 fix: actual_response should be the transaction-mapped body, not raw.
    # Response rules: rename cst_name→name, delete debug_flag.
    assert "<name>张三</name>" in saved_kwargs["actual_response"]
    assert "<cst_name>" not in saved_kwargs["actual_response"]
    assert "<debug_flag>" not in saved_kwargs["actual_response"]


@pytest.mark.asyncio
async def test_list_results_includes_source_recording_context():
    replay_result = SimpleNamespace(
        id=101,
        job_id=11,
        test_case_id=22,
        status="PENDING",
        request_method="POST",
        request_uri="/api/bank/service",
        actual_status_code=None,
        actual_response=None,
        expected_response=None,
        diff_result=None,
        diff_score=None,
        assertion_results=None,
        is_pass=False,
        latency_ms=None,
        failure_category=None,
        failure_reason=None,
        created_at=datetime.now(timezone.utc),
    )
    job = SimpleNamespace(use_sub_invocation_mocks=True)
    test_case = SimpleNamespace(source_recording_id=33)
    recording = SimpleNamespace(
        transaction_code="OPEN_ACCOUNT",
        scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
        sub_calls='[{"type":"MySQL"},{"type":"Redis"}]',
    )

    class DummyRows:
        def __init__(self, rows):
            self._rows = rows

        def all(self):
            return self._rows

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[
        DummyRows([(replay_result, "OPEN_ACCOUNT")]),
        DummyResult(job),
        DummyResult(test_case),
        DummyResult(recording),
    ])

    rows = await list_results(job_id=11, status=None, skip=0, limit=50, db=db, _=None)
    assert len(rows) == 1
    out = rows[0]
    assert out.use_sub_invocation_mocks is True
    assert out.source_recording_id == 33
    assert out.source_recording_transaction_code == "OPEN_ACCOUNT"
    assert out.source_recording_scene_key == "OPEN_ACCOUNT|POST|/api/bank/service|success"
    assert out.source_recording_sub_call_count == 2
    assert out.transaction_code == "OPEN_ACCOUNT"


@pytest.mark.asyncio
async def test_get_replay_result_includes_source_recording_context():
    replay_result = SimpleNamespace(
        id=102,
        job_id=12,
        test_case_id=23,
        status="PENDING",
        request_method="GET",
        request_uri="/api/bank/service",
        actual_status_code=None,
        actual_response=None,
        expected_response=None,
        diff_result=None,
        diff_score=None,
        assertion_results=None,
        is_pass=False,
        latency_ms=None,
        failure_category=None,
        failure_reason=None,
        created_at=datetime.now(timezone.utc),
    )
    job = SimpleNamespace(use_sub_invocation_mocks=False)
    test_case = SimpleNamespace(source_recording_id=44)
    recording = SimpleNamespace(
        transaction_code=None,
        scene_key=None,
        sub_calls='[{"type":"MySQL"},{"type":"Redis"},{"type":"RPC"}]',
    )

    class DummyResult:
        def __init__(self, value):
            self.value = value

        def scalar_one_or_none(self):
            return self.value

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[
        DummyResult(replay_result),
        DummyResult(None),
        DummyResult(job),
        DummyResult(test_case),
        DummyResult(recording),
    ])

    out = await get_replay_result(result_id=102, db=db, _=None)
    assert out.use_sub_invocation_mocks is False
    assert out.source_recording_id == 44
    assert out.source_recording_transaction_code is None
    assert out.source_recording_scene_key is None
    assert out.source_recording_sub_call_count == 3


@pytest.mark.asyncio
async def test_get_html_report_includes_mock_and_source_recording_summary():
    job = SimpleNamespace(
        id=201,
        name="Replay job",
        application_id=1,
        status="DONE",
        concurrency=2,
        timeout_ms=5000,
        passed=0,
        failed=1,
        errored=0,
        total=1,
        ignore_fields='["timestamp"]',
        diff_rules='[{"type":"ignore"}]',
        assertions='[{"type":"status_code_eq"}]',
        use_sub_invocation_mocks=True,
        started_at=datetime(2026, 4, 14, 10, 0, 0, tzinfo=timezone.utc),
        finished_at=datetime(2026, 4, 14, 10, 1, 0, tzinfo=timezone.utc),
    )
    result = SimpleNamespace(
        id=301,
        job_id=201,
        test_case_id=401,
        status="FAIL",
        request_method="POST",
        request_uri="/api/bank/service",
        actual_status_code=200,
        actual_response='{"code": 0}',
        expected_response='{"code": 1}',
        diff_result='{"code":{"values_changed":{"old_value":1,"new_value":0}}}',
        diff_score=0.5,
        assertion_results='[{"passed": false, "message": "status mismatch"}]',
        is_pass=False,
        latency_ms=123,
        failure_category="response_diff",
        failure_reason="body diff",
        created_at=datetime(2026, 4, 14, 10, 0, 30, tzinfo=timezone.utc),
    )
    test_case = SimpleNamespace(
        id=401,
        transaction_code="OPEN_ACCOUNT",
        request_body='{"service_id":"OPEN_ACCOUNT"}',
        source_recording_id=501,
    )
    app = SimpleNamespace(name="uat-bank-service")
    recording = SimpleNamespace(
        id=501,
        transaction_code="OPEN_ACCOUNT",
        scene_key="OPEN_ACCOUNT|POST|/api/bank/service|success",
        sub_calls='[{"type":"MySQL"},{"type":"Redis"}]',
    )

    class DummyResult:
        def __init__(self, value=None, values=None):
            self.value = value
            self.values = values or []

        def scalar_one_or_none(self):
            return self.value

        def scalars(self):
            return self

        def all(self):
            return self.values

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[
        DummyResult(job),
        DummyResult(values=[result]),
        DummyResult(app),
        DummyResult(values=[test_case]),
        DummyResult(recording),
    ])

    response = await get_html_report(job_id=201, db=db, _=None)
    html = response.body.decode("utf-8")
    assert "子调用 Mock" in html
    assert "来源录制" in html
    assert "OPEN_ACCOUNT" in html
    assert "录制 #501" in html
    assert "子调用 2" in html
    assert "filterStatus('ALL', event)" in html


@pytest.mark.asyncio
async def test_run_replay_job_applies_active_compare_rules(client, admin_headers, created_app):
    rule_resp = client.post(
        "/api/v1/compare-rules",
        json={
            "name": "ignore-timestamp",
            "scope": "global",
            "rule_type": "ignore",
            "config": '{"path": "timestamp"}',
            "is_active": True,
        },
        headers=admin_headers,
    )
    assert rule_resp.status_code == 201

    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "compare-rule-case",
            "application_id": created_app["id"],
            "request_method": "GET",
            "request_uri": "/compare",
            "expected_response": '{"timestamp": 1000, "value": "ok"}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job = _create_replay_job(client, admin_headers, [tc["id"]], application_id=created_app["id"]).json()

    class DummyResponse:
        status_code = 200
        text = '{"timestamp": 9999, "value": "ok"}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()
        job_row = (
            await db.execute(select(ReplayJob).where(ReplayJob.id == job["id"]))
        ).scalar_one()
    assert result_row.status == "PASS"
    assert result_row.failure_category is None
    assert job_row.status == "DONE"


@pytest.mark.asyncio
async def test_run_replay_job_applies_job_ignore_fields_and_header_transforms(client, admin_headers, created_app):
    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "ignore-field-case",
            "application_id": created_app["id"],
            "request_method": "GET",
            "request_uri": "/headers",
            "request_headers": '{"X-Test": "old"}',
            "expected_response": '{"timestamp": 1000, "value": "ok"}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job = _create_replay_job(
        client,
        admin_headers,
        [tc["id"]],
        application_id=created_app["id"],
        ignore_fields=["timestamp"],
        header_transforms=[
            {"type": "replace", "key": "X-Test", "value": "new"},
            {"type": "add", "key": "X-Added", "value": "1"},
        ],
    ).json()

    class DummyResponse:
        status_code = 200
        text = '{"timestamp": 9999, "value": "ok"}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await run_replay_job(job["id"])

    _, kwargs = request_mock.await_args
    assert kwargs["headers"]["X-Test"] == "new"
    assert kwargs["headers"]["X-Added"] == "1"

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()
    assert result_row.status == "PASS"


@pytest.mark.asyncio
async def test_run_replay_job_fails_on_expected_status_mismatch(client, admin_headers, created_app):
    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "status-mismatch-case",
            "application_id": created_app["id"],
            "request_method": "GET",
            "request_uri": "/status",
            "expected_status": 201,
            "expected_response": '{"ok": true}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job = _create_replay_job(client, admin_headers, [tc["id"]], application_id=created_app["id"]).json()

    class DummyResponse:
        status_code = 200
        text = '{"ok": true}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()
        job_row = (
            await db.execute(select(ReplayJob).where(ReplayJob.id == job["id"]))
        ).scalar_one()
    assert result_row.status == "FAIL"
    assert result_row.failure_category == "status_mismatch"
    assert "期望 201" in (result_row.failure_reason or "")
    assert job_row.status == "FAILED"


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


@pytest.mark.asyncio
async def test_run_replay_job_response_diff_failure_reason_includes_changed_path(client, admin_headers, created_app):
    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "xml-diff-case",
            "application_id": created_app["id"],
            "request_method": "POST",
            "request_uri": "/api/bank/service",
            "expected_response": '{"body": {"account_no": "6222", "customer_no": "C001"}}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job = _create_replay_job(client, admin_headers, [tc["id"]], application_id=created_app["id"]).json()

    class DummyResponse:
        status_code = 200
        text = '{"body": {"account_no": "6333", "customer_no": "C001"}}'

    request_mock = AsyncMock(return_value=DummyResponse())
    with patch("httpx.AsyncClient.request", request_mock):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()
    assert result_row.status == "FAIL"
    assert result_row.failure_category == "response_diff"
    assert "body.account_no" in (result_row.failure_reason or "")


def test_create_replay_job_with_repeat_count(client, admin_headers, tc_payload):
    """repeat_count 能通过 API 保存并回显。"""
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        repeat_count=3,
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["repeat_count"] == 3


def test_create_replay_job_with_target_host(client, admin_headers, tc_payload):
    """target_host 能通过 API 保存并回显。"""
    tc = _create_test_case(client, admin_headers, tc_payload)
    resp = _create_replay_job(
        client, admin_headers, [tc["id"]],
        target_host="http://custom-host:8080",
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["target_host"] == "http://custom-host:8080"


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_empty(tmp_path):
    """When no ArexMocker rows exist for record_id, returns None."""
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await _fetch_replay_sub_calls("nonexistent-id")
        assert result is None
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_returns_json(tmp_path):
    """When ArexMocker rows exist, returns JSON string of sub-calls."""
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.arex_mocker import ArexMocker as MockerModel

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t2.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    mocker_data = json.dumps({
        "categoryType": {"name": "MySQL", "entryPoint": False},
        "operationName": "SELECT * FROM car_policy",
        "targetRequest": {"body": {"sql": "SELECT * FROM car_policy"}},
        "targetResponse": {"body": {"rows": [{"id": 1}]}},
    })
    async with factory() as session:
        session.add(MockerModel(
            record_id="replay-001",
            app_id="didi-car-uat",
            category_name="MySQL",
            is_entry_point=False,
            mocker_data=mocker_data,
        ))
        await session.commit()

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await _fetch_replay_sub_calls("replay-001")
        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["type"] == "MySQL"
        assert parsed[0]["operation"] == "SELECT * FROM car_policy"
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_normalizes_repository_dynamic_class(tmp_path):
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.arex_mocker import ArexMocker as MockerModel

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t3.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    mocker_data = json.dumps({
        "categoryType": {"name": "DynamicClass", "entryPoint": False},
        "operationName": "com.arex.demo.didi.common.repository.CarDataRepository.findDispatch",
        "targetRequest": {"body": json.dumps(["沪A12345", "GAR001"])},
        "targetResponse": {"body": json.dumps({"dispatch_no": "D001", "city": "SH"})},
    })
    async with factory() as session:
        session.add(MockerModel(
            record_id="replay-002",
            app_id="didi-car-uat",
            category_name="DynamicClass",
            is_entry_point=False,
            mocker_data=mocker_data,
        ))
        await session.commit()

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await _fetch_replay_sub_calls("replay-002")
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["type"] == "MySQL"
        assert parsed[0]["source"] == "agent"
        assert parsed[0]["table"] == "car_dispatch"
        assert parsed[0]["operation"] == "SELECT car_dispatch"
        assert parsed[0]["params"]["garageCode"] == "GAR001"
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_enriches_didi_reconstructed_sub_calls(tmp_path):
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.application import Application
    from models.test_case import TestCase

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t4.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with factory() as session:
        app = Application(
            name="didi-system-a",
            ssh_host="127.0.0.1",
            ssh_user="test",
            ssh_port=22,
            service_port=18081,
            arex_app_id="didi-car-sat",
        )
        session.add(app)
        await session.flush()
        case = TestCase(
            name="case-1",
            application_id=app.id,
            request_method="POST",
            request_uri="/api/car/service",
            request_body="<request><code>car000001</code><request_no>REQ-car000001</request_no><customer_no>C10001</customer_no><plate_no>沪A10001</plate_no></request>",
            expected_status=200,
            expected_response="{}",
        )
        session.add(case)
        await session.commit()
        await session.refresh(case)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with (
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch(
                "utils.replay_sub_call_fetch.get_plugin_for_app_id",
                return_value=MagicMock(
                    fetch_extra_sub_calls=AsyncMock(return_value=[{
                        "type": "MySQL",
                        "operation": "INSERT car_order_audit",
                        "table": "car_order_audit",
                        "response": {"request_no": "REQ-car000001"},
                        "status": "WRITE",
                    }])
                ),
            ),
        ):
            result = await _fetch_replay_sub_calls("replay-003", case=case)
        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["operation"] == "INSERT car_order_audit"
        assert parsed[0]["status"] == "WRITE"
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_enriches_didi_reconstructed_sub_calls_without_arex_record_id(tmp_path):
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.application import Application
    from models.test_case import TestCase

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t5.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with factory() as session:
        app = Application(
            name="didi-system-a",
            ssh_host="127.0.0.1",
            ssh_user="test",
            ssh_port=22,
            service_port=18081,
            arex_app_id="didi-car-sat",
        )
        session.add(app)
        await session.flush()
        case = TestCase(
            name="case-1",
            application_id=app.id,
            request_method="POST",
            request_uri="/api/car/service",
            request_body="<request><code>car000001</code><request_no>REQ-car000001</request_no><customer_no>C10001</customer_no><plate_no>沪A10001</plate_no></request>",
            expected_status=200,
            expected_response="{}",
        )
        session.add(case)
        await session.commit()
        await session.refresh(case)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        with patch(
            "utils.replay_sub_call_fetch.get_plugin_for_app_id",
            return_value=MagicMock(
                fetch_extra_sub_calls=AsyncMock(return_value=[{
                    "type": "MySQL",
                    "operation": "INSERT car_order_audit",
                    "table": "car_order_audit",
                    "response": {"request_no": "REQ-car000001"},
                    "status": "WRITE",
                }])
            ),
        ):
            result = await _fetch_replay_sub_calls(None, case=case)
        assert result is not None
        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["operation"] == "INSERT car_order_audit"
        assert parsed[0]["status"] == "WRITE"
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


@pytest.mark.asyncio
async def test_fetch_replay_sub_calls_recovers_sibling_internal_http_sub_calls_without_arex_record_id(tmp_path):
    import database as db_module
    from sqlalchemy.pool import NullPool
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from models.application import Application
    from models.arex_mocker import ArexMocker as MockerModel
    from models.test_case import TestCase

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/t6.db", poolclass=NullPool)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    from database import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with factory() as session:
        app = Application(
            name="didi-system-a",
            ssh_host="127.0.0.1",
            ssh_user="test",
            ssh_port=22,
            service_port=18081,
            arex_app_id="didi-car-sat",
        )
        session.add(app)
        await session.flush()
        case = TestCase(
            name="case-1",
            application_id=app.id,
            request_method="POST",
            request_uri="/api/car/service",
            request_body=(
                "<request><tra_id>912359029940924300</tra_id><code>car000001</code>"
                "<request_no>REQ-car000001</request_no><customer_no>C10001</customer_no>"
                "<plate_no>沪A10001</plate_no></request>"
            ),
            expected_status=200,
            expected_response="{}",
        )
        session.add(case)
        session.add_all([
            MockerModel(
                record_id="SIB-001",
                app_id="didi-car-sat",
                category_name="Servlet",
                is_entry_point=True,
                created_at_ms=1002,
                mocker_data=json.dumps({
                    "operationName": "/internal/didi/risk",
                    "targetRequest": {
                        "attributes": {
                            "HttpMethod": "GET",
                            "RequestPath": "/internal/didi/risk?traId=912359029940924300&txnCode=car000001&customerNo=C10001",
                        },
                    },
                    "targetResponse": {
                        "body": json.dumps({"txnCode": "car000001", "riskLevel": "LOW"}),
                        "attributes": {"Headers": {"arex-record-id": "SIB-001"}},
                    },
                }, ensure_ascii=False),
            ),
            MockerModel(
                record_id="SIB-002",
                app_id="didi-car-sat",
                category_name="Servlet",
                is_entry_point=True,
                created_at_ms=1008,
                mocker_data=json.dumps({
                    "operationName": "/internal/didi/pricing",
                    "targetRequest": {
                        "attributes": {
                            "HttpMethod": "GET",
                            "RequestPath": "/internal/didi/pricing?traId=912359029940924300&txnCode=car000001&customerNo=VIP",
                        },
                    },
                    "targetResponse": {
                        "body": json.dumps({"txnCode": "car000001", "quoteAmount": 294.4}),
                        "attributes": {"Headers": {"arex-record-id": "SIB-002"}},
                    },
                }, ensure_ascii=False),
            ),
            MockerModel(
                record_id="OTHER-001",
                app_id="didi-car-sat",
                category_name="Servlet",
                is_entry_point=True,
                created_at_ms=1005,
                mocker_data=json.dumps({
                    "operationName": "/internal/didi/risk",
                    "targetRequest": {
                        "attributes": {
                            "HttpMethod": "GET",
                            "RequestPath": "/internal/didi/risk?traId=999999999999999999&txnCode=car000015&customerNo=C10001",
                        },
                    },
                    "targetResponse": {
                        "body": json.dumps({"txnCode": "car000015", "riskLevel": "LOW"}),
                        "attributes": {"Headers": {"arex-record-id": "OTHER-001"}},
                    },
                }, ensure_ascii=False),
            ),
        ])
        await session.commit()
        await session.refresh(case)

    original_factory = db_module.async_session_factory
    db_module.async_session_factory = factory
    try:
        from core.replay_executor import _fetch_replay_sub_calls
        from utils.didi_plugin import DidiPlugin
        with patch("utils.replay_sub_call_fetch.get_plugin_for_app_id", return_value=DidiPlugin()):
            result = await _fetch_replay_sub_calls(None, case=case, anchor_created_at_ms=1005)
        assert result is not None
        parsed = json.loads(result)
        assert [item["operation"] for item in parsed] == [
            "/internal/didi/risk",
            "/internal/didi/pricing",
        ]
        assert all(item["type"] == "HttpClient" for item in parsed)
        assert all(item["source"] == "sibling_servlet" for item in parsed)
        assert all(item["method"] == "GET" for item in parsed)
        assert parsed[0]["response"]["httpStatus"] == 200
        assert parsed[0]["response"]["body"]["txnCode"] == "car000001"
        assert parsed[1]["response"]["headers"]["arex-record-id"] == ["SIB-002"]
    finally:
        db_module.async_session_factory = original_factory
        await engine.dispose()


def test_sub_call_diff_not_found(client, admin_headers):
    resp = client.get("/api/v1/replays/results/99999/sub-call-diff", headers=admin_headers)
    assert resp.status_code == 404


def test_sub_call_diff_no_sub_calls(client, admin_headers, tc_payload):
    tc = _create_test_case(client, admin_headers, tc_payload)
    job_resp = _create_replay_job(client, admin_headers, [tc["id"]])
    assert job_resp.status_code == 201
    job_id = job_resp.json()["id"]

    results_resp = client.get(f"/api/v1/replays/{job_id}/results", headers=admin_headers)
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert len(results) >= 1
    result_id = results[0]["id"]

    resp = client.get(f"/api/v1/replays/results/{result_id}/sub-call-diff", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "recorded" in data
    assert "replayed" in data
    assert "pairs" in data
    assert data["replayed"] == []


def test_pair_sub_calls_both_sides():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    replayed = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 2}}]
    pairs = _pair_sub_calls(recorded, replayed)
    assert len(pairs) == 1
    assert pairs[0]["side"] == "both"
    assert pairs[0]["response_matched"] is False


def test_pair_sub_calls_recorded_only():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    pairs = _pair_sub_calls(recorded, [])
    assert len(pairs) == 1
    assert pairs[0]["side"] == "recorded_only"
    assert pairs[0]["response_matched"] is None


def test_pair_sub_calls_replayed_only():
    from api.v1.replays import _pair_sub_calls
    replayed = [{"type": "MySQL", "operation": "SELECT 2", "response": {"rows": 3}}]
    pairs = _pair_sub_calls([], replayed)
    assert len(pairs) == 1
    assert pairs[0]["side"] == "replayed_only"
    assert pairs[0]["response_matched"] is None


def test_pair_sub_calls_response_matched_true():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    replayed = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    pairs = _pair_sub_calls(recorded, replayed)
    assert len(pairs) == 1
    assert pairs[0]["response_matched"] is True


def test_pair_sub_calls_treats_numeric_strings_as_equal():
    from api.v1.replays import _pair_sub_calls
    recorded = [{
        "type": "MySQL",
        "operation": "SELECT car_vehicle",
        "response": {"risk_score": "42", "premium_amount": "1880.00"},
    }]
    replayed = [{
        "type": "MySQL",
        "operation": "SELECT car_vehicle",
        "response": {"risk_score": 42, "premium_amount": 1880},
    }]

    pairs = _pair_sub_calls(recorded, replayed)

    assert len(pairs) == 1
    assert pairs[0]["side"] == "both"
    assert pairs[0]["response_matched"] is True


def test_pair_sub_calls_unequal_lengths():
    from api.v1.replays import _pair_sub_calls
    recorded = [
        {"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}},
        {"type": "HTTP", "operation": "/api/risk", "response": {"score": 10}},
    ]
    replayed = [{"type": "MySQL", "operation": "SELECT 1", "response": {"rows": 1}}]
    pairs = _pair_sub_calls(recorded, replayed)
    assert len(pairs) == 2
    assert pairs[0]["side"] == "both"
    assert pairs[1]["side"] == "recorded_only"


def test_pair_sub_calls_matches_by_type_and_operation_not_index():
    from api.v1.replays import _pair_sub_calls
    recorded = [
        {"type": "MySQL", "operation": "SELECT car_vehicle", "response": {"plateNo": "A"}},
        {"type": "HttpClient", "operation": "/internal/didi/risk", "response": {"riskLevel": "LOW"}},
    ]
    replayed = [
        {"type": "HttpClient", "operation": "/internal/didi/risk", "response": {"riskLevel": "LOW"}},
        {"type": "MySQL", "operation": "SELECT car_vehicle", "response": {"plateNo": "B"}},
    ]

    pairs = _pair_sub_calls(recorded, replayed)

    assert len(pairs) == 2
    assert pairs[0]["type"] == "MySQL"
    assert pairs[0]["recorded"]["operation"] == "SELECT car_vehicle"
    assert pairs[0]["replayed"]["operation"] == "SELECT car_vehicle"
    assert pairs[0]["response_matched"] is False
    assert pairs[1]["type"] == "HttpClient"
    assert pairs[1]["recorded"]["operation"] == "/internal/didi/risk"
    assert pairs[1]["replayed"]["operation"] == "/internal/didi/risk"
    assert pairs[1]["response_matched"] is True


def test_pair_sub_calls_keeps_distinct_types_unpaired():
    from api.v1.replays import _pair_sub_calls
    recorded = [{"type": "MySQL", "operation": "SELECT car_vehicle", "response": {"rows": 1}}]
    replayed = [{"type": "HttpClient", "operation": "/internal/didi/risk", "response": {"riskLevel": "LOW"}}]

    pairs = _pair_sub_calls(recorded, replayed)

    assert len(pairs) == 2
    assert pairs[0]["side"] == "recorded_only"
    assert pairs[0]["type"] == "MySQL"
    assert pairs[1]["side"] == "replayed_only"
    assert pairs[1]["type"] == "HttpClient"


def test_pair_sub_calls_prefers_same_request_when_operation_repeats():
    from api.v1.replays import _pair_sub_calls
    recorded = [
        {
            "type": "MySQL",
            "operation": "SELECT car_vehicle",
            "request": {"plateNo": "沪A10001"},
            "response": {"vehicle_status": "ACTIVE"},
        },
        {
            "type": "MySQL",
            "operation": "SELECT car_vehicle",
            "request": {"plateNo": "沪A10002"},
            "response": {"vehicle_status": "INACTIVE"},
        },
    ]
    replayed = [
        {
            "type": "MySQL",
            "operation": "SELECT car_vehicle",
            "request": {"plateNo": "沪A10002"},
            "response": {"vehicle_status": "INACTIVE"},
        },
        {
            "type": "MySQL",
            "operation": "SELECT car_vehicle",
            "request": {"plateNo": "沪A10001"},
            "response": {"vehicle_status": "ACTIVE"},
        },
    ]

    pairs = _pair_sub_calls(recorded, replayed)

    assert len(pairs) == 2
    assert pairs[0]["recorded"]["request"]["plateNo"] == "沪A10001"
    assert pairs[0]["replayed"]["request"]["plateNo"] == "沪A10001"
    assert pairs[1]["recorded"]["request"]["plateNo"] == "沪A10002"
    assert pairs[1]["replayed"]["request"]["plateNo"] == "沪A10002"
