"""Async replay executor: send requests concurrently, compare responses."""
import asyncio
import json
import logging
import time
from typing import Optional

import httpx
from sqlalchemy import select

from database import async_session_factory
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from models.application import Application
from utils.diff import compute_diff
from utils.assertions import evaluate_assertions, assertions_all_passed
from config import settings

logger = logging.getLogger(__name__)

# Active jobs: job_id -> set of WebSocket connections for progress push
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
    async with async_session_factory() as db:
        result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            logger.warning(f"ReplayJob {job_id} not found")
            return

        # Get test cases from the job's case list stored in diff_rules field
        # Actually case_ids were stored separately; we need to look them up via results
        # Get ALL results for this job to find case IDs
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

        # Load test cases
        cases_result = await db.execute(
            select(TestCase).where(TestCase.id.in_(case_ids))
        )
        cases = cases_result.scalars().all()
        case_map = {c.id: c for c in cases}

        # Determine target host
        target_host = None
        if job.application_id:
            app_result = await db.execute(
                select(Application).where(Application.id == job.application_id)
            )
            app = app_result.scalar_one_or_none()
            if app:
                target_host = f"http://{app.ssh_host}:{app.service_port}"

        # Update job status
        from datetime import datetime, timezone
        job.status = "RUNNING"
        job.total = len(case_ids)
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

    # Parse job config
    diff_rules = None
    assertions_config = None
    try:
        if job.diff_rules:
            diff_rules = json.loads(job.diff_rules)
        if job.assertions:
            assertions_config = json.loads(job.assertions)
    except Exception:
        pass

    # Run concurrently
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
                case=case,
                target_host=target_host,
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

        await _broadcast_progress(job_id, {
            "job_id": job_id,
            "done": done_count,
            "total": job.total,
            "passed": passed,
            "failed": failed,
            "errored": errored,
        })

    await asyncio.gather(*[_run_one(cid) for cid in case_ids])

    # Finalize
    async with async_session_factory() as db:
        from datetime import datetime, timezone
        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            # Set status to FAILED if no cases passed and there are failures/errors
            if passed == 0 and (failed > 0 or errored > 0):
                job.status = "FAILED"
            else:
                job.status = "DONE"
            job.passed = passed
            job.failed = failed
            job.errored = errored
            job.finished_at = datetime.now(timezone.utc)
            await db.commit()

    await _broadcast_progress(job_id, {
        "job_id": job_id,
        "done": done_count,
        "total": done_count,
        "passed": passed,
        "failed": failed,
        "errored": errored,
        "finished": True,
    })


async def _execute_single(
    job_id: int,
    case: Optional[TestCase],
    target_host: Optional[str],
    timeout_ms: int,
    diff_rules,
    assertions_config,
    perf_threshold_ms: Optional[int],
    use_mocks: bool,
) -> ReplayResult:
    """Execute one test case and save result to DB."""
    from datetime import datetime, timezone

    if not case:
        async with async_session_factory() as db:
            r = ReplayResult(
                job_id=job_id,
                status="ERROR",
                is_pass=False,
                failure_category="connection_error",
                failure_reason="Test case not found",
            )
            db.add(r)
            await db.commit()
            await db.refresh(r)
            return r

    # Build request URL
    base_url = target_host or "http://localhost:8080"
    url = f"{base_url}{case.request_uri}"

    # Parse headers
    headers = {}
    if case.request_headers:
        try:
            headers = json.loads(case.request_headers)
        except Exception:
            pass

    # Remove host header to avoid conflicts
    headers = {k: v for k, v in headers.items() if k.lower() not in ("host", "content-length")}

    # Execute request
    start = time.monotonic()
    actual_status = None
    actual_body = None
    status = "ERROR"
    failure_category = None
    failure_reason = None

    try:
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
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        status = "ERROR"
        failure_category = "connection_error"
        failure_reason = str(e)

    # Compute diff
    diff_json = None
    diff_score = None
    assertion_results_json = None
    is_pass = False

    if status == "OK_GOT_RESPONSE":
        # Parse ignore fields
        ignore_fields = []
        if case.ignore_fields:
            try:
                ignore_fields = json.loads(case.ignore_fields)
            except Exception:
                pass

        diff_json, diff_score = compute_diff(
            original=case.expected_response,
            replayed=actual_body,
            diff_rules=diff_rules,
            ignore_fields=ignore_fields,
        )

        # Evaluate assertions
        combined_assertions = []
        if assertions_config:
            combined_assertions.extend(assertions_config)
        if case.assert_rules:
            try:
                combined_assertions.extend(json.loads(case.assert_rules))
            except Exception:
                pass

        assertion_results = evaluate_assertions(
            assertions=combined_assertions,
            replayed_body=actual_body,
            status_code=actual_status,
            diff_score=diff_score,
        )
        assertion_results_json = json.dumps(assertion_results, ensure_ascii=False)

        # Determine pass/fail
        diff_ok = diff_json is None  # no diff
        assertions_ok = assertions_all_passed(assertion_results)
        perf_ok = (perf_threshold_ms is None) or (latency_ms <= perf_threshold_ms)

        if diff_ok and assertions_ok and perf_ok:
            status = "PASS"
            is_pass = True
        else:
            status = "FAIL"
            failure_category = "diff" if not diff_ok else ("assertion" if not assertions_ok else "performance")
            failure_reason = "Response mismatch" if not diff_ok else ("Assertion failed" if not assertions_ok else f"Latency {latency_ms}ms > threshold {perf_threshold_ms}ms")

    # Save result
    async with async_session_factory() as db:
        r = ReplayResult(
            job_id=job_id,
            test_case_id=case.id,
            status=status,
            request_method=case.request_method,
            request_uri=case.request_uri,
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
        db.add(r)
        await db.commit()
        await db.refresh(r)
        return r
