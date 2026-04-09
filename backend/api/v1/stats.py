"""Statistics API for dashboard and reporting."""
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case

from database import get_db
from models.replay import ReplayJob, ReplayResult
from models.application import Application
from models.test_case import TestCase
from core.security import require_viewer

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/trend")
async def get_pass_rate_trend(
    days: int = Query(7, ge=1, le=90),
    application_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    Return daily pass rate for the last N days.
    Response: [{"date": "2026-04-01", "total": 100, "passed": 90, "pass_rate": 0.9}]
    """
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    stmt = select(ReplayJob).where(
        and_(
            ReplayJob.created_at >= start,
            ReplayJob.status == "DONE",
        )
    )
    if application_id:
        stmt = stmt.where(ReplayJob.application_id == application_id)

    result = await db.execute(stmt)
    jobs = result.scalars().all()

    # Group by date
    from collections import defaultdict
    daily: dict[str, dict] = defaultdict(lambda: {"total": 0, "passed": 0})
    for job in jobs:
        date_str = job.created_at.strftime("%Y-%m-%d")
        daily[date_str]["total"] += job.total or 0
        daily[date_str]["passed"] += job.passed or 0

    # Fill in missing days
    trend = []
    for i in range(days):
        d = (end - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        entry = daily.get(d, {"total": 0, "passed": 0})
        pass_rate = (entry["passed"] / entry["total"]) if entry["total"] > 0 else None
        trend.append({
            "date": d,
            "total": entry["total"],
            "passed": entry["passed"],
            "pass_rate": round(pass_rate, 4) if pass_rate is not None else None,
        })
    return trend


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    Overall summary: total apps, test cases, replay jobs (last 30 days), average pass rate.
    Response: {"apps": 5, "test_cases": 120, "recent_jobs": 30, "avg_pass_rate": 0.92}
    """
    apps_count = (await db.execute(select(func.count()).select_from(Application))).scalar()
    cases_count = (await db.execute(select(func.count()).select_from(TestCase))).scalar()

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    jobs_result = await db.execute(
        select(ReplayJob).where(
            and_(ReplayJob.created_at >= thirty_days_ago, ReplayJob.status == "DONE")
        )
    )
    recent_jobs = jobs_result.scalars().all()
    total_cases_run = sum(j.total or 0 for j in recent_jobs)
    total_passed = sum(j.passed or 0 for j in recent_jobs)
    avg_pass_rate = (total_passed / total_cases_run) if total_cases_run > 0 else None

    return {
        "apps": apps_count,
        "test_cases": cases_count,
        "recent_jobs": len(recent_jobs),
        "avg_pass_rate": round(avg_pass_rate, 4) if avg_pass_rate is not None else None,
    }


@router.get("/app-summary")
async def get_app_summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    Per-application summary.
    Response: [{"app_id": 1, "app_name": "demo", "test_cases": 20, "recent_pass_rate": 0.85}]
    """
    apps_result = await db.execute(select(Application))
    apps = apps_result.scalars().all()

    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    summaries = []
    for app in apps:
        # Count test cases
        tc_count = (
            await db.execute(
                select(func.count()).select_from(TestCase).where(TestCase.application_id == app.id)
            )
        ).scalar()

        # Recent jobs
        jobs_result = await db.execute(
            select(ReplayJob).where(
                and_(
                    ReplayJob.application_id == app.id,
                    ReplayJob.created_at >= thirty_days_ago,
                    ReplayJob.status == "DONE",
                )
            )
        )
        jobs = jobs_result.scalars().all()
        total = sum(j.total or 0 for j in jobs)
        passed = sum(j.passed or 0 for j in jobs)
        pass_rate = (passed / total) if total > 0 else None

        summaries.append({
            "app_id": app.id,
            "app_name": app.name,
            "agent_status": app.agent_status,
            "test_cases": tc_count,
            "recent_jobs": len(jobs),
            "recent_pass_rate": round(pass_rate, 4) if pass_rate is not None else None,
        })
    return summaries


@router.get("/failure-types")
async def get_failure_types(
    days: int = Query(7, ge=1, le=90),
    application_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    Failure type distribution for the last N days.
    Response: [{"category": "diff", "count": 45}, {"category": "assertion", "count": 12}]
    """
    start = datetime.now(timezone.utc) - timedelta(days=days)

    # Join results with jobs to filter by date and application
    stmt = (
        select(ReplayResult.failure_category, func.count().label("count"))
        .join(ReplayJob, ReplayResult.job_id == ReplayJob.id)
        .where(
            and_(
                ReplayJob.created_at >= start,
                ReplayResult.is_pass == False,
                ReplayResult.failure_category.isnot(None),
            )
        )
    )
    if application_id:
        stmt = stmt.where(ReplayJob.application_id == application_id)

    stmt = stmt.group_by(ReplayResult.failure_category)
    result = await db.execute(stmt)
    rows = result.all()

    return [{"category": row[0], "count": row[1]} for row in rows]


@router.get("/recent-jobs")
async def get_recent_jobs(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Return most recent replay jobs with basic stats."""
    stmt = (
        select(ReplayJob)
        .where(ReplayJob.status.in_(["DONE", "FAILED", "RUNNING"]))
        .order_by(ReplayJob.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    jobs = result.scalars().all()
    return [
        {
            "id": j.id,
            "name": j.name,
            "status": j.status,
            "total": j.total,
            "passed": j.passed,
            "failed": j.failed,
            "pass_rate": round(j.passed / j.total, 4) if j.total and j.total > 0 else None,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]
