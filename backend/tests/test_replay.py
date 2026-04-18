"""Tests for replay job creation, execution, result query, and report rendering."""
import asyncio
import json
from types import SimpleNamespace
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from api.v1.replays import _build_result_source_context, _count_sub_call_nodes
from api.v1.replays import get_html_report, get_replay_result, list_results
from core.replay_executor import _execute_single, run_replay_job
import database
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
    recording = SimpleNamespace(record_id="mock-record-1")

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
        transaction_code="A0201M14I",
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
            "transaction_code": "A0201M14I",
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
    assert saved_kwargs["actual_response"] == "<response><cst_name>张三</cst_name><debug_flag>1</debug_flag></response>"


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
    app = SimpleNamespace(name="vt-bank-service")
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
