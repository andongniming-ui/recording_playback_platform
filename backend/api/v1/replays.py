"""Replay job management API."""
import asyncio
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.replay_context import infer_application_id_for_case_ids
from core.replay_executor import register_ws, unregister_ws
from core.security import require_editor, require_viewer
from database import async_session_factory, get_db
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from schemas.replay import ReplayJobCreate, ReplayJobOut, ReplayResultOut

router = APIRouter(prefix="/replays", tags=["replays"])


@router.post("", response_model=ReplayJobOut, status_code=201)
async def create_replay_job(
    body: ReplayJobCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Create and start a replay job."""
    if not body.case_ids:
        raise HTTPException(status_code=400, detail="case_ids must not be empty")

    from sqlalchemy import func

    count_result = await db.execute(
        select(func.count()).select_from(TestCase).where(TestCase.id.in_(body.case_ids))
    )
    found_count = count_result.scalar()
    if found_count != len(body.case_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Some case_ids do not exist: expected {len(body.case_ids)}, found {found_count}",
        )

    try:
        inferred_application_id = await infer_application_id_for_case_ids(db, body.case_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    application_id = body.application_id
    if inferred_application_id is not None:
        if application_id is not None and application_id != inferred_application_id:
            raise HTTPException(
                status_code=400,
                detail="application_id does not match the selected test cases",
            )
        application_id = inferred_application_id

    job = ReplayJob(
        name=body.name,
        application_id=application_id,
        status="PENDING",
        concurrency=body.concurrency,
        timeout_ms=body.timeout_ms,
        total=len(body.case_ids),
        use_sub_invocation_mocks=body.use_sub_invocation_mocks,
        diff_rules=body.diff_rules,
        assertions=body.assertions,
        perf_threshold_ms=body.perf_threshold_ms,
        webhook_url=body.webhook_url,
        notify_type=body.notify_type,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in body.case_ids:
        db.add(
            ReplayResult(
                job_id=job.id,
                test_case_id=case_id,
                status="PENDING",
                is_pass=False,
            )
        )
    await db.commit()

    import core.replay_executor as replay_executor

    asyncio.create_task(replay_executor.run_replay_job(job.id))
    return job


@router.get("", response_model=list[ReplayJobOut])
async def list_replay_jobs(
    application_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(ReplayJob)
    if application_id:
        stmt = stmt.where(ReplayJob.application_id == application_id)
    stmt = stmt.order_by(ReplayJob.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{job_id}", response_model=ReplayJobOut)
async def get_replay_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")
    return job


@router.get("/{job_id}/results", response_model=list[ReplayResultOut])
async def list_results(
    job_id: int,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(ReplayResult).where(ReplayResult.job_id == job_id)
    if status:
        stmt = stmt.where(ReplayResult.status == status)
    stmt = stmt.order_by(ReplayResult.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{job_id}/report", response_class=HTMLResponse)
async def get_html_report(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Generate a standalone HTML report for a replay job."""
    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results_query = await db.execute(
        select(ReplayResult).where(ReplayResult.job_id == job_id).order_by(ReplayResult.id)
    )
    results = results_query.scalars().all()

    pass_rate = f"{(job.passed / job.total * 100):.1f}%" if job.total > 0 else "-"
    job_status_label = {
        "PENDING": "\u5f85\u6267\u884c",
        "RUNNING": "\u8fd0\u884c\u4e2d",
        "DONE": "\u5df2\u5b8c\u6210",
        "FAILED": "\u5931\u8d25",
        "CANCELLED": "\u5df2\u53d6\u6d88",
    }.get(job.status, job.status)
    result_status_label = {
        "PASS": "\u901a\u8fc7",
        "FAIL": "\u5931\u8d25",
        "ERROR": "\u5f02\u5e38",
        "TIMEOUT": "\u8d85\u65f6",
        "PENDING": "\u5f85\u6267\u884c",
    }
    failure_type_label = {
        "assertion_failed": "\u65ad\u8a00\u5931\u8d25",
        "status_mismatch": "\u72b6\u6001\u7801\u4e0d\u4e00\u81f4",
        "response_diff": "\u54cd\u5e94\u5185\u5bb9\u4e0d\u4e00\u81f4",
        "timeout": "\u8bf7\u6c42\u8d85\u65f6",
        "connection_error": "\u8fde\u63a5\u5f02\u5e38",
        "mock_error": "Mock \u5f02\u5e38",
    }

    rows = ""
    for result in results:
        color = "green" if result.is_pass else "red"
        latency = f"{result.latency_ms}ms" if result.latency_ms is not None else "-"
        rows += f"""
        <tr>
            <td>{result.id}</td>
            <td>{result.request_method or '-'} {result.request_uri or '-'}</td>
            <td style="color:{color}">{result_status_label.get(result.status, result.status)}</td>
            <td>{result.actual_status_code or '-'}</td>
            <td>{latency}</td>
            <td>{failure_type_label.get(result.failure_category or '', result.failure_category or '-')}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AREX \u5f55\u5236\u5e73\u53f0 - \u56de\u653e\u62a5\u544a #{job_id}</title>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>\u56de\u653e\u62a5\u544a #{job_id}\uff1a{job.name or '-'}</h1>
    <div class="summary">
        <strong>\u4efb\u52a1\u72b6\u6001\uff1a</strong> {job_status_label} |
        <strong>\u603b\u6570\uff1a</strong> {job.total} |
        <strong>\u901a\u8fc7\uff1a</strong> {job.passed} |
        <strong>\u5931\u8d25\uff1a</strong> {job.failed} |
        <strong>\u5f02\u5e38\uff1a</strong> {job.errored} |
        <strong>\u901a\u8fc7\u7387\uff1a</strong> {pass_rate}
    </div>
    <table>
        <thead>
            <tr><th>ID</th><th>\u8bf7\u6c42\u4fe1\u606f</th><th>\u6267\u884c\u7ed3\u679c</th><th>\u54cd\u5e94\u7801</th><th>\u8017\u65f6</th><th>\u5931\u8d25\u7c7b\u578b</th></tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>
</body>
</html>"""
    return html


@router.websocket("/{job_id}/ws")
async def replay_progress_ws(job_id: int, websocket: WebSocket):
    """WebSocket endpoint for real-time replay progress."""
    await websocket.accept()
    register_ws(job_id, websocket)
    try:
        async with async_session_factory() as db:
            result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                await websocket.send_json(
                    {
                        "job_id": job_id,
                        "done": job.passed + job.failed + job.errored,
                        "total": job.total,
                        "passed": job.passed,
                        "failed": job.failed,
                        "errored": job.errored,
                        "finished": job.status in ("DONE", "FAILED", "CANCELLED"),
                    }
                )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        unregister_ws(job_id, websocket)
