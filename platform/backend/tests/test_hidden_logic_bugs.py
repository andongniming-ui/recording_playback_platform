"""
TDD tests for 3 hidden logic bugs in replay_executor.py.

Bug 1 – set-based greedy sub-call matching is non-deterministic (contract test only;
         set iterates ascending in CPython so it passes by accident – fix makes it
         explicit).
Bug 2 – job.total local variable not updated after repeat_count multiplication →
         _broadcast_progress broadcasts stale total.
Bug 3 – _save_result overwrites first failure reason when retry also fails →
         original failure_category / failure_reason is lost.
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from unittest.mock import AsyncMock, patch

import database
from models.recording import Recording
from core.replay_executor import run_replay_job, _save_result


# ---------------------------------------------------------------------------
# Bug 1 – greedy sub-call matching: position-based contract test
# ---------------------------------------------------------------------------


def test_build_sub_call_diff_pairs_matches_positionally_for_duplicate_operations():
    """When two expected calls share the same type+operation, each should match
    the actual call at the same position (first-available), not an arbitrary one."""
    from core.replay_executor import _build_sub_call_diff_pairs

    # Two identical-operation MySQL calls but with distinct responses A and B
    expected = json.dumps([
        {"type": "MySQL", "operation": "SELECT item", "response": {"id": 1, "name": "A"}},
        {"type": "MySQL", "operation": "SELECT item", "response": {"id": 2, "name": "B"}},
    ])
    # Actual matches positionally (A→A, B→B)
    actual = json.dumps([
        {"type": "MySQL", "operation": "SELECT item", "response": {"id": 1, "name": "A"}},
        {"type": "MySQL", "operation": "SELECT item", "response": {"id": 2, "name": "B"}},
    ])

    pairs = _build_sub_call_diff_pairs(expected, actual)

    # Both pairs should match with no diff
    assert len(pairs) == 2
    assert all(p["matched"] for p in pairs)
    assert all(not p["has_diff"] for p in pairs), (
        f"Expected no diff when responses match positionally, got {pairs}"
    )


# ---------------------------------------------------------------------------
# Bug 2 – job.total stale in _broadcast_progress when repeat_count > 1
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_broadcast_progress_uses_expanded_total_when_repeat_count_gt_1(
    client, admin_headers, created_app
):
    """When repeat_count=3, case_ids is tripled → total should be 3 in broadcasts,
    not the original 1 stored in job.total before expansion."""

    # Create a session + recording
    async with database.async_session_factory() as db:
        session_resp = client.post(
            "/api/v1/sessions",
            json={"application_id": created_app["id"], "name": "repeat-test-session"},
            headers=admin_headers,
        )
        session_id = session_resp.json()["id"]

        recording = Recording(
            session_id=session_id,
            application_id=created_app["id"],
            request_method="GET",
            request_uri="/ping",
            request_body="",
            response_status=200,
            response_body='{"ok": true}',
            record_id="REC-REPEAT-001",
            dedupe_hash="repeat-test-001",
        )
        db.add(recording)
        await db.commit()
        await db.refresh(recording)

    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "repeat-tc",
            "application_id": created_app["id"],
            "request_method": "GET",
            "request_uri": "/ping",
            "expected_response": '{"ok": true}',
            "source_recording_id": recording.id,
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    # Create a job with repeat_count=3 (total starts as 1, should expand to 3)
    job_resp = client.post(
        "/api/v1/replays",
        json={
            "case_ids": [tc["id"]],
            "application_id": created_app["id"],
            "repeat_count": 3,
            "use_sub_invocation_mocks": False,
        },
        headers=admin_headers,
    )
    assert job_resp.status_code == 201
    job = job_resp.json()

    broadcast_totals = []

    async def _capture_broadcast(job_id, data):
        broadcast_totals.append(data.get("total"))

    class DummyResponse:
        status_code = 200
        text = '{"ok": true}'
        headers = {}

    with (
        patch("httpx.AsyncClient.request", AsyncMock(return_value=DummyResponse())),
        patch("core.replay_executor._broadcast_progress", side_effect=_capture_broadcast),
        patch("core.replay_executor._fetch_replay_sub_calls", AsyncMock(return_value=None)),
    ):
        await run_replay_job(job["id"])

    # Every progress broadcast should report total=3 (expanded), not 1 (stale)
    assert broadcast_totals, "Expected at least one _broadcast_progress call"
    stale_broadcasts = [t for t in broadcast_totals if t != 3]
    assert not stale_broadcasts, (
        f"Got stale total values in broadcasts: {broadcast_totals} "
        f"(expected all 3, bug shows {stale_broadcasts})"
    )


# ---------------------------------------------------------------------------
# Bug 3 – _save_result overwrites first failure reason on retry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_save_result_preserves_first_failure_reason_on_retry(
    client, admin_headers, created_app
):
    """When a test case fails and is retried (also fails), the original failure
    reason from the first attempt should be preserved, not overwritten."""

    tc_resp = client.post(
        "/api/v1/test-cases",
        json={
            "name": "retry-preserve-tc",
            "application_id": created_app["id"],
            "request_method": "POST",
            "request_uri": "/order/submit",
            "expected_response": '{"status": "OK"}',
        },
        headers=admin_headers,
    )
    assert tc_resp.status_code == 201
    tc = tc_resp.json()

    job_resp = client.post(
        "/api/v1/replays",
        json={"case_ids": [tc["id"]], "application_id": created_app["id"]},
        headers=admin_headers,
    )
    assert job_resp.status_code == 201
    job = job_resp.json()

    # First attempt: fails with a specific reason
    await _save_result(
        job["id"],
        tc["id"],
        status="FAIL",
        is_pass=False,
        failure_category="response_mismatch",
        failure_reason="差异字段: amount (expected 100, got 200)",
    )

    # Second attempt (retry): fails with a different reason
    r2 = await _save_result(
        job["id"],
        tc["id"],
        status="FAIL",
        is_pass=False,
        failure_category="timeout",
        failure_reason="请求超时",
    )

    # The ORIGINAL failure reason should be preserved
    assert r2.failure_reason == "差异字段: amount (expected 100, got 200)", (
        f"Expected original failure_reason preserved after retry, got: {r2.failure_reason!r}"
    )
    assert r2.failure_category == "response_mismatch", (
        f"Expected original failure_category preserved after retry, got: {r2.failure_category!r}"
    )
