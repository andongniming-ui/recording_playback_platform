"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import json
import logging
import time
from typing import Optional

import httpx
from sqlalchemy import select

from config import settings
import database
from integration.arex_client import ArexClient, ArexClientError
from models.application import Application
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from utils.assertions import assertions_all_passed, evaluate_assertions
from utils.diff import compute_diff

logger = logging.getLogger(__name__)

_ws_connections: dict[int, set] = {}


def register_ws(job_id: int, ws):
    _ws_connections.setdefault(job_id, set()).add(ws)


def unregister_ws(job_id: int, ws):
    if job_id in _ws_connections:
        _ws_connections[job_id].discard(ws)


async def _broadcast_progress(job_id: int, data: dict):
    conns = _ws_connections.get(job_id, set())
    dead = set()
    for ws in conns:
        try:
            await ws.send_json(data)
        except Exception:
            dead.add(ws)
    for ws in dead:
        conns.discard(ws)


async def run_replay_job(job_id: int):
    """Main entry point: run a replay job from DB state."""
    async with database.async_session_factory() as db:
        result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning("ReplayJob %s not found", job_id)
            return

        results_query = await db.execute(
            select(ReplayResult.test_case_id)
            .where(ReplayResult.job_id == job_id)
            .where(ReplayResult.test_case_id.isnot(None))
        )
        case_ids = list(results_query.scalars().all())

        if not case_ids:
            job.status = "DONE"
            job.total = 0
            await db.commit()
            return

        cases_result = await db.execute(select(TestCase).where(TestCase.id.in_(case_ids)))
        cases = cases_result.scalars().all()
        case_map = {case.id: case for case in cases}

        resolved_application_id = job.application_id
        if resolved_application_id is None:
            case_application_ids = {case.application_id for case in cases if case.application_id is not None}
            if len(case_application_ids) == 1:
                resolved_application_id = next(iter(case_application_ids))
                job.application_id = resolved_application_id

        target_host = None
        arex_storage_url = settings.arex_storage_url
        if resolved_application_id:
            app_result = await db.execute(
                select(Application).where(Application.id == resolved_application_id)
            )
            app = app_result.scalar_one_or_none()
            if app:
                target_host = f"http://{app.ssh_host}:{app.service_port}"
                arex_storage_url = app.arex_storage_url or settings.arex_storage_url

        from datetime import datetime, timezone

        job.status = "RUNNING"
        job.total = len(case_ids)
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

    diff_rules = None
    assertions_config = None
    try:
        if job.diff_rules:
            diff_rules = json.loads(job.diff_rules)
        if job.assertions:
            assertions_config = json.loads(job.assertions)
    except Exception:
        logger.warning("ReplayJob %s has invalid diff_rules/assertions JSON", job_id)

    semaphore = asyncio.Semaphore(job.concurrency)
    done_count = 0
    passed = 0
    failed = 0
    errored = 0

    async def _run_one(case_id: int):
        nonlocal done_count, passed, failed, errored
        case = case_map.get(case_id)
        async with semaphore:
            result = await _execute_single(
                job_id=job_id,
                case_id=case_id,
                case=case,
                target_host=target_host,
                arex_storage_url=arex_storage_url,
                timeout_ms=job.timeout_ms,
                diff_rules=diff_rules,
                assertions_config=assertions_config,
                perf_threshold_ms=job.perf_threshold_ms,
                use_mocks=job.use_sub_invocation_mocks,
            )

        done_count += 1
        if result.status == "PASS":
            passed += 1
        elif result.status in ("FAIL", "TIMEOUT"):
            failed += 1
        else:
            errored += 1

        await _broadcast_progress(
            job_id,
            {
                "job_id": job_id,
                "done": done_count,
                "total": job.total,
                "passed": passed,
                "failed": failed,
                "errored": errored,
            },
        )

    await asyncio.gather(*[_run_one(case_id) for case_id in case_ids])

    async with database.async_session_factory() as db:
        from datetime import datetime, timezone

        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            job.status = "FAILED" if failed > 0 or errored > 0 else "DONE"
            job.passed = passed
            job.failed = failed
            job.errored = errored
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()

    await _broadcast_progress(
        job_id,
        {
            "job_id": job_id,
            "done": done_count,
            "total": done_count,
            "passed": passed,
            "failed": failed,
            "errored": errored,
            "finished": True,
        },
    )


async def _execute_single(
    job_id: int,
    case_id: int,
    case: Optional[TestCase],
    target_host: Optional[str],
    arex_storage_url: str,
    timeout_ms: int,
    diff_rules,
    assertions_config,
    perf_threshold_ms: Optional[int],
    use_mocks: bool,
) -> ReplayResult:
    """Execute one test case and save the result back into the placeholder row."""
    if not case:
        return await _save_result(
            job_id=job_id,
            case_id=case_id,
            status="ERROR",
            is_pass=False,
            failure_category="connection_error",
            failure_reason="Test case not found",
        )

    mock_record_id = None
    if use_mocks:
        if not case.source_recording_id:
            return await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="use_sub_invocation_mocks requires a test case created from a recording",
            )
        async with database.async_session_factory() as db:
            recording_result = await db.execute(
                select(Recording).where(Recording.id == case.source_recording_id)
            )
            recording = recording_result.scalar_one_or_none()
        if not recording or not recording.record_id:
            return await _save_result(
                job_id=job_id,
                case_id=case_id,
                case=case,
                status="ERROR",
                is_pass=False,
                failure_category="mock_error",
                failure_reason="Source recording not found or missing AREX record_id",
            )
        mock_record_id = recording.record_id

    base_url = target_host or "http://localhost:8080"
    url = f"{base_url}{case.request_uri}"

    headers = {}
    if case.request_headers:
        try:
            headers = json.loads(case.request_headers)
        except Exception:
            logger.warning("Replay case %s has invalid request_headers JSON", case.id)
    headers = {
        key: value
        for key, value in headers.items()
        if key.lower() not in ("host", "content-length")
    }

    start = time.monotonic()
    actual_status = None
    actual_body = None
    status = "ERROR"
    failure_category = None
    failure_reason = None
    mock_client = ArexClient(arex_storage_url)
    mock_loaded = False

    try:
        if use_mocks and mock_record_id:
            await mock_client.cache_load_mock(mock_record_id)
            mock_loaded = True

        timeout = httpx.Timeout(timeout_ms / 1000.0)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.request(
                method=case.request_method or "GET",
                url=url,
                content=case.request_body.encode() if case.request_body else None,
                headers=headers,
            )
        actual_status = resp.status_code
        actual_body = resp.text
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "OK_GOT_RESPONSE"
    except httpx.TimeoutException:
        latency_ms = timeout_ms
        status = "TIMEOUT"
        failure_category = "timeout"
        failure_reason = f"Request timed out after {timeout_ms}ms"
    except ArexClientError as exc:
        latency_ms = 0
        status = "ERROR"
        failure_category = "mock_error"
        failure_reason = str(exc)
    except Exception as exc:
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "ERROR"
        failure_category = "connection_error"
        failure_reason = str(exc)
    finally:
        if mock_loaded and mock_record_id:
            try:
                await mock_client.cache_remove_mock(mock_record_id)
            except Exception as exc:
                logger.warning("Failed to remove AREX mock cache for %s: %s", mock_record_id, exc)

    diff_json = None
    diff_score = None
    assertion_results_json = None
    is_pass = False

    if status == "OK_GOT_RESPONSE":
        ignore_fields = []
        if case.ignore_fields:
            try:
                ignore_fields = json.loads(case.ignore_fields)
            except Exception:
                logger.warning("Replay case %s has invalid ignore_fields JSON", case.id)

        diff_json, diff_score = compute_diff(
            original=case.expected_response,
            replayed=actual_body,
            diff_rules=diff_rules,
            ignore_fields=ignore_fields,
        )

        combined_assertions = []
        if assertions_config:
            combined_assertions.extend(assertions_config)
        if case.assert_rules:
            try:
                combined_assertions.extend(json.loads(case.assert_rules))
            except Exception:
                logger.warning("Replay case %s has invalid assert_rules JSON", case.id)

        assertion_results = evaluate_assertions(
            assertions=combined_assertions,
            replayed_body=actual_body,
            status_code=actual_status,
            diff_score=diff_score,
        )
        assertion_results_json = json.dumps(assertion_results, ensure_ascii=False)

        diff_ok = diff_json is None
        assertions_ok = assertions_all_passed(assertion_results)
        perf_ok = perf_threshold_ms is None or latency_ms <= perf_threshold_ms

        if diff_ok and assertions_ok and perf_ok:
            status = "PASS"
            is_pass = True
        else:
            status = "FAIL"
            failure_category = (
                "diff"
                if not diff_ok
                else ("assertion" if not assertions_ok else "performance")
            )
            failure_reason = (
                "Response mismatch"
                if not diff_ok
                else (
                    "Assertion failed"
                    if not assertions_ok
                    else f"Latency {latency_ms}ms > threshold {perf_threshold_ms}ms"
                )
            )

    return await _save_result(
        job_id=job_id,
        case_id=case_id,
        case=case,
        status=status,
        actual_status_code=actual_status,
        actual_response=actual_body,
        expected_response=case.expected_response,
        diff_result=diff_json,
        assertion_results=assertion_results_json,
        is_pass=is_pass,
        latency_ms=latency_ms,
        failure_category=failure_category,
        failure_reason=failure_reason,
    )


async def _save_result(
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
    assertion_results: Optional[str] = None,
    latency_ms: Optional[int] = None,
    failure_category: Optional[str] = None,
    failure_reason: Optional[str] = None,
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
        replay_result.assertion_results = assertion_results
        replay_result.is_pass = is_pass
        replay_result.latency_ms = latency_ms
        replay_result.failure_category = failure_category
        replay_result.failure_reason = failure_reason

        await db.commit()
        await db.refresh(replay_result)
        return replay_result
