"""
TDD tests for P1 fix: fail_on_sub_call_diff option on ReplayJob.

When enabled, sub-call differences (missing, extra, or response mismatch)
should cause the replay result to be marked FAIL instead of PASS.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import database
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from models.recording import Recording
# Import at module level so the reference is captured before conftest patches it
from core.replay_executor import run_replay_job


# ---------------------------------------------------------------------------
# Model / Schema: fail_on_sub_call_diff field exists
# ---------------------------------------------------------------------------


def test_replay_job_model_has_fail_on_sub_call_diff_field():
    """ReplayJob ORM model must have a fail_on_sub_call_diff Boolean column."""
    from models.replay import ReplayJob
    assert hasattr(ReplayJob, "fail_on_sub_call_diff"), (
        "ReplayJob model is missing fail_on_sub_call_diff field"
    )


def test_replay_job_create_schema_accepts_fail_on_sub_call_diff():
    """ReplayJobCreate schema must accept fail_on_sub_call_diff=True."""
    from schemas.replay import ReplayJobCreate
    schema = ReplayJobCreate(
        case_ids=[1],
        fail_on_sub_call_diff=True,
    )
    assert schema.fail_on_sub_call_diff is True


def test_replay_job_create_schema_defaults_fail_on_sub_call_diff_to_false():
    from schemas.replay import ReplayJobCreate
    schema = ReplayJobCreate(case_ids=[1])
    assert schema.fail_on_sub_call_diff is False


def test_replay_job_out_schema_includes_fail_on_sub_call_diff():
    """ReplayJobOut must expose fail_on_sub_call_diff so the frontend can read it."""
    from schemas.replay import ReplayJobOut
    import inspect
    fields = ReplayJobOut.model_fields
    assert "fail_on_sub_call_diff" in fields, (
        "ReplayJobOut schema is missing fail_on_sub_call_diff field"
    )


# ---------------------------------------------------------------------------
# Helper: _sub_calls_have_diff
# ---------------------------------------------------------------------------


def test_sub_calls_have_diff_returns_false_when_both_empty():
    from core.replay_executor import _sub_calls_have_diff
    assert _sub_calls_have_diff(None, None) is False
    assert _sub_calls_have_diff("[]", "[]") is False


def test_sub_calls_have_diff_returns_true_when_counts_differ():
    from core.replay_executor import _sub_calls_have_diff
    expected = json.dumps([{"type": "MySQL", "operation": "SELECT customer", "response": {"id": 1}}])
    actual = json.dumps([])
    assert _sub_calls_have_diff(expected, actual) is True


def test_sub_calls_have_diff_returns_true_when_response_differs():
    from core.replay_executor import _sub_calls_have_diff
    expected = json.dumps([{
        "type": "MySQL", "operation": "SELECT customer",
        "request": {"customerId": "C001"},
        "response": {"age": 30, "status": "ACTIVE"},
    }])
    actual = json.dumps([{
        "type": "MySQL", "operation": "SELECT customer",
        "request": {"customerId": "C001"},
        "response": {"age": 35, "status": "ACTIVE"},   # age changed
    }])
    assert _sub_calls_have_diff(expected, actual) is True


def test_sub_calls_have_diff_returns_false_when_responses_match():
    from core.replay_executor import _sub_calls_have_diff
    sub = json.dumps([{
        "type": "MySQL", "operation": "SELECT customer",
        "request": {"customerId": "C001"},
        "response": {"age": 30, "status": "ACTIVE"},
    }])
    assert _sub_calls_have_diff(sub, sub) is False


def test_sub_calls_have_diff_returns_true_when_extra_actual_call():
    from core.replay_executor import _sub_calls_have_diff
    expected = json.dumps([{"type": "MySQL", "operation": "SELECT customer"}])
    actual = json.dumps([
        {"type": "MySQL", "operation": "SELECT customer"},
        {"type": "HTTP", "operation": "POST /extra"},   # extra call in replay
    ])
    assert _sub_calls_have_diff(expected, actual) is True


def test_strict_sub_call_failure_detects_missing_actual_sub_calls():
    from core.replay_executor import _strict_sub_call_failure

    expected = json.dumps([{"type": "MySQL", "operation": "SELECT customer"}])
    failure = _strict_sub_call_failure(
        expected_sub_calls_json=expected,
        actual_sub_calls_json=None,
    )

    assert failure is not None
    assert failure[0] == "sub_call_missing"


# ---------------------------------------------------------------------------
# HttpClient sub-calls should not trigger strict failure (unreliable in replay)
# ---------------------------------------------------------------------------


def test_strict_sub_call_failure_ignores_missing_httpclient_only():
    """HttpClient-only missing sub-calls must NOT trigger failure."""
    from core.replay_executor import _strict_sub_call_failure

    expected = json.dumps([{"type": "HttpClient", "operation": "/order/query"}])
    failure = _strict_sub_call_failure(
        expected_sub_calls_json=expected,
        actual_sub_calls_json=None,
    )
    assert failure is None, (
        "HttpClient-only missing sub-call should not trigger FAIL"
    )


def test_strict_sub_call_failure_still_fails_when_database_missing():
    """Database missing sub-calls must still trigger failure even with HttpClient present."""
    from core.replay_executor import _strict_sub_call_failure

    expected = json.dumps([
        {"type": "Database", "operation": "query"},
        {"type": "HttpClient", "operation": "/order/query"},
    ])
    failure = _strict_sub_call_failure(
        expected_sub_calls_json=expected,
        actual_sub_calls_json=None,
    )
    assert failure is not None, (
        "Database missing sub-call must still trigger FAIL"
    )
    assert failure[0] == "sub_call_missing"


def test_strict_sub_call_failure_passes_when_only_httpclient_missing_from_mixed():
    """Database present + HttpClient missing → should PASS."""
    from core.replay_executor import _strict_sub_call_failure

    expected = json.dumps([
        {"type": "Database", "operation": "query", "response": [{"id": 1}]},
        {"type": "HttpClient", "operation": "/order/query"},
    ])
    actual = json.dumps([
        {"type": "Database", "operation": "query", "response": [{"id": 1}]},
        # HttpClient missing from actual — should be ignored
    ])
    failure = _strict_sub_call_failure(
        expected_sub_calls_json=expected,
        actual_sub_calls_json=actual,
    )
    assert failure is None, (
        "HttpClient missing from actual with Database matching should not FAIL"
    )


def test_filter_sub_calls_for_strict_check_removes_httpclient():
    from core.replay_executor import _filter_sub_calls_for_strict_check
    import json

    sub_calls = json.dumps([
        {"type": "Database", "operation": "query"},
        {"type": "HttpClient", "operation": "/order/query"},
        {"type": "http", "operation": "/other"},
    ])
    result = _filter_sub_calls_for_strict_check(sub_calls)
    parsed = json.loads(result)
    assert len(parsed) == 1
    assert parsed[0]["type"] == "Database"


def test_filter_sub_calls_for_strict_check_returns_none_when_all_httpclient():
    from core.replay_executor import _filter_sub_calls_for_strict_check

    sub_calls = json.dumps([{"type": "HttpClient", "operation": "/foo"}])
    result = _filter_sub_calls_for_strict_check(sub_calls)
    assert result is None


# ---------------------------------------------------------------------------
# Integration: fail_on_sub_call_diff=True triggers FAIL when sub-calls differ
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_fail_on_sub_call_diff_true_downgrades_pass_to_fail(client, admin_headers, created_app):
    """When fail_on_sub_call_diff=True and sub-calls differ, PASS → FAIL."""

    # Create a recording with expected sub-calls
    async with database.async_session_factory() as db:
        session_resp = client.post(
            "/api/v1/sessions",
            json={"application_id": created_app["id"], "name": "sub-diff-session"},
            headers=admin_headers,
        )
        session_id = session_resp.json()["id"]

        recording = Recording(
            session_id=session_id,
            application_id=created_app["id"],
            request_method="POST",
            request_uri="/loan/gateway",
            request_body='{"customerId": "C001"}',
            response_status=200,
            response_body='{"result": "APPROVED"}',
            record_id="REC-LOAN-001",
            sub_calls=json.dumps([{
                "type": "MySQL",
                "operation": "SELECT customer",
                "request": {"customerId": "C001"},
                "response": {"age": 30, "status": "ACTIVE"},
            }]),
            dedupe_hash="loan-sub-diff-001",
        )
        db.add(recording)
        await db.commit()
        await db.refresh(recording)

    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "loan-sub-diff-case",
            "application_id": created_app["id"],
            "request_method": "POST",
            "request_uri": "/loan/gateway",
            "request_body": '{"customerId": "C001"}',
            "expected_response": '{"result": "APPROVED"}',
            "source_recording_id": recording.id,
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job_resp = client.post(
        "/api/v1/replays",
        json={
            "case_ids": [tc["id"]],
            "application_id": created_app["id"],
            "fail_on_sub_call_diff": True,
            "use_sub_invocation_mocks": False,
        },
        headers=admin_headers,
    )
    assert job_resp.status_code == 201
    job = job_resp.json()
    assert job["fail_on_sub_call_diff"] is True

    # Actual response matches → would normally PASS
    # But actual sub-calls differ (age=35 instead of 30) → should FAIL
    actual_sub_calls_differ = json.dumps([{
        "type": "MySQL",
        "operation": "SELECT customer",
        "request": {"customerId": "C001"},
        "response": {"age": 35, "status": "ACTIVE"},   # difference!
    }])

    class DummyResponse:
        status_code = 200
        text = '{"result": "APPROVED"}'
        headers = {"arex-record-id": "REC-LOAN-001"}

    request_mock = AsyncMock(return_value=DummyResponse())

    async def _fake_fetch_sub_calls(record_id, case=None, anchor_created_at_ms=None):
        return actual_sub_calls_differ

    with patch("httpx.AsyncClient.request", request_mock), \
         patch("core.replay_executor._fetch_replay_sub_calls", _fake_fetch_sub_calls):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()

    assert result_row.status == "FAIL", (
        f"Expected FAIL when sub-calls differ with fail_on_sub_call_diff=True, got {result_row.status}"
    )
    assert result_row.failure_category == "sub_call_diff"


@pytest.mark.asyncio
async def test_fail_on_sub_call_diff_false_keeps_pass_when_sub_calls_differ(client, admin_headers, created_app):
    """When fail_on_sub_call_diff=False, sub-call differences remain display-only."""

    async with database.async_session_factory() as db:
        session_resp = client.post(
            "/api/v1/sessions",
            json={"application_id": created_app["id"], "name": "sub-nodiff-session"},
            headers=admin_headers,
        )
        session_id = session_resp.json()["id"]

        recording = Recording(
            session_id=session_id,
            application_id=created_app["id"],
            request_method="POST",
            request_uri="/loan/gateway",
            request_body='{"customerId": "C002"}',
            response_status=200,
            response_body='{"result": "APPROVED"}',
            record_id="REC-LOAN-002",
            sub_calls=json.dumps([{"type": "MySQL", "operation": "SELECT customer"}]),
            dedupe_hash="loan-sub-nodiff-001",
        )
        db.add(recording)
        await db.commit()
        await db.refresh(recording)

    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "loan-sub-nodiff-case",
            "application_id": created_app["id"],
            "request_method": "POST",
            "request_uri": "/loan/gateway",
            "expected_response": '{"result": "APPROVED"}',
            "source_recording_id": recording.id,
        },
        headers=admin_headers,
    )
    tc = tc_resp.json()

    job_resp = client.post(
        "/api/v1/replays",
        json={
            "case_ids": [tc["id"]],
            "application_id": created_app["id"],
            "fail_on_sub_call_diff": False,
        },
        headers=admin_headers,
    )
    job = job_resp.json()

    different_sub_calls = json.dumps([
        {"type": "MySQL", "operation": "SELECT customer"},
        {"type": "HTTP", "operation": "POST /extra"},   # extra call
    ])

    class DummyResponse:
        status_code = 200
        text = '{"result": "APPROVED"}'
        headers = {}

    with patch("httpx.AsyncClient.request", AsyncMock(return_value=DummyResponse())), \
         patch("core.replay_executor._fetch_replay_sub_calls", AsyncMock(return_value=different_sub_calls)):
        await run_replay_job(job["id"])

    async with database.async_session_factory() as db:
        result_row = (
            await db.execute(select(ReplayResult).where(ReplayResult.job_id == job["id"]))
        ).scalar_one()

    assert result_row.status == "PASS", (
        f"Expected PASS when fail_on_sub_call_diff=False, got {result_row.status}"
    )

