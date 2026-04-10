"""Replay job management API."""
import asyncio
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db, async_session_factory
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from schemas.replay import ReplayJobCreate, ReplayJobOut, ReplayResultOut
from core.security import require_viewer, require_editor, get_current_user
from core.replay_executor import run_replay_job, register_ws, unregister_ws

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

    # Validate all case_ids exist
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

    job = ReplayJob(
        name=body.name,
        application_id=body.application_id,
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

    # Pre-create result placeholders so executor can find case_ids
    for case_id in body.case_ids:
        r = ReplayResult(
            job_id=job.id,
            test_case_id=case_id,
            status="PENDING",
            is_pass=False,
        )
        db.add(r)
    await db.commit()

    # Start async execution
    asyncio.create_task(run_replay_job(job.id))

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
async def get_replay_job(job_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_viewer)):
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
async def get_html_report(job_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_viewer)):
    """Generate a standalone HTML report for a replay job."""
    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results_query = await db.execute(
        select(ReplayResult).where(ReplayResult.job_id == job_id).order_by(ReplayResult.id)
    )
    results = results_query.scalars().all()

    pass_rate = f"{(job.passed / job.total * 100):.1f}%" if job.total > 0 else "N/A"

    rows = ""
    for r in results:
        color = "green" if r.is_pass else "red"
        rows += f"""
        <tr>
            <td>{r.id}</td>
            <td>{r.request_method or '-'} {r.request_uri or '-'}</td>
            <td style="color:{color}">{r.status}</td>
            <td>{r.actual_status_code or '-'}</td>
            <td>{r.latency_ms or '-'}ms</td>
            <td>{r.failure_category or '-'}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>AREX Recorder - Replay Report #{job_id}</title>
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
    <h1>回放报告 #{job_id}: {job.name or '-'}</h1>
    <div class="summary">
        <strong>状态：</strong>{job.status} |
        <strong>总数：</strong>{job.total} |
        <strong>通过：</strong>{job.passed} |
        <strong>失败：</strong>{job.failed} |
        <strong>错误：</strong>{job.errored} |
        <strong>通过率：</strong>{pass_rate}
    </div>
    <table>
        <thead>
            <tr><th>ID</th><th>请求</th><th>状态</th><th>HTTP状态码</th><th>延迟</th><th>失败原因</th></tr>
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
        # Send current job state immediately
        async with async_session_factory() as db:
            result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                await websocket.send_json({
                    "job_id": job_id,
                    "done": job.passed + job.failed + job.errored,
                    "total": job.total,
                    "passed": job.passed,
                    "failed": job.failed,
                    "errored": job.errored,
                    "finished": job.status in ("DONE", "FAILED", "CANCELLED"),
                })
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        pass
    finally:
        unregister_ws(job_id, websocket)
