"""Replay result persistence helpers."""

from typing import Optional

from sqlalchemy import select

import database
from models.replay import ReplayResult
from models.test_case import TestCase


async def save_result(
    job_id: int,
    case_id: int,
    *,
    case: Optional[TestCase] = None,
    status: str,
    is_pass: bool,
    actual_status_code: Optional[int] = None,
    actual_response: Optional[str] = None,
    expected_response: Optional[str] = None,
    diff_result: Optional[str] = None,
    diff_score: Optional[float] = None,
    assertion_results: Optional[str] = None,
    latency_ms: Optional[int] = None,
    failure_category: Optional[str] = None,
    failure_reason: Optional[str] = None,
    actual_sub_calls: Optional[str] = None,
    sub_call_diff_detail: Optional[str] = None,
) -> ReplayResult:
    """Update the placeholder replay result for a case, or create one if missing."""
    async with database.async_session_factory() as db:
        result = await db.execute(
            select(ReplayResult)
            .where(ReplayResult.job_id == job_id, ReplayResult.test_case_id == case_id)
            .order_by(ReplayResult.id)
        )
        replay_result = result.scalars().first()

        if replay_result is None:
            replay_result = ReplayResult(
                job_id=job_id,
                test_case_id=case_id,
                status="PENDING",
                is_pass=False,
            )
            db.add(replay_result)

        replay_result.status = status
        replay_result.request_method = case.request_method if case else None
        replay_result.request_uri = case.request_uri if case else None
        replay_result.actual_status_code = actual_status_code
        replay_result.actual_response = actual_response
        replay_result.expected_response = expected_response
        replay_result.diff_result = diff_result
        replay_result.diff_score = diff_score
        replay_result.assertion_results = assertion_results
        replay_result.is_pass = is_pass
        replay_result.latency_ms = latency_ms
        if is_pass:
            replay_result.failure_category = None
            replay_result.failure_reason = None
        elif not replay_result.failure_reason:
            replay_result.failure_category = failure_category
            replay_result.failure_reason = failure_reason
        replay_result.actual_sub_calls = actual_sub_calls
        replay_result.sub_call_diff_detail = sub_call_diff_detail

        await db.commit()
        await db.refresh(replay_result)
        return replay_result


_save_result = save_result
