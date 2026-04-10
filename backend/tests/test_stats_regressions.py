"""Regression tests for dashboard statistics."""
from datetime import datetime, timedelta, timezone

import pytest

import database
from models.replay import ReplayJob


@pytest.mark.asyncio
async def test_stats_summary_and_app_summary_include_failed_jobs(client, admin_headers, created_app):
    now = datetime.now(timezone.utc)

    async with database.async_session_factory() as db:
        db.add_all(
            [
                ReplayJob(
                    name="done-job",
                    application_id=created_app["id"],
                    status="DONE",
                    total=10,
                    passed=8,
                    failed=2,
                    errored=0,
                    created_at=now - timedelta(days=1),
                ),
                ReplayJob(
                    name="failed-job",
                    application_id=created_app["id"],
                    status="FAILED",
                    total=10,
                    passed=3,
                    failed=6,
                    errored=1,
                    created_at=now - timedelta(days=2),
                ),
            ]
        )
        await db.commit()

    summary_resp = client.get("/api/v1/stats/summary", headers=admin_headers)
    assert summary_resp.status_code == 200
    summary = summary_resp.json()
    assert summary["recent_jobs"] == 2
    assert summary["avg_pass_rate"] == 0.55

    app_summary_resp = client.get("/api/v1/stats/app-summary", headers=admin_headers)
    assert app_summary_resp.status_code == 200
    app_summary = app_summary_resp.json()
    assert len(app_summary) == 1
    assert app_summary[0]["recent_jobs"] == 2
    assert app_summary[0]["recent_pass_rate"] == 0.55


@pytest.mark.asyncio
async def test_stats_trend_includes_failed_jobs(client, admin_headers, created_app):
    now = datetime.now(timezone.utc)
    job_day = (now - timedelta(days=1)).date()

    async with database.async_session_factory() as db:
        db.add_all(
            [
                ReplayJob(
                    name="trend-done",
                    application_id=created_app["id"],
                    status="DONE",
                    total=4,
                    passed=4,
                    failed=0,
                    errored=0,
                    created_at=datetime.combine(job_day, datetime.min.time(), tzinfo=timezone.utc),
                ),
                ReplayJob(
                    name="trend-failed",
                    application_id=created_app["id"],
                    status="FAILED",
                    total=6,
                    passed=3,
                    failed=2,
                    errored=1,
                    created_at=datetime.combine(job_day, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=1),
                ),
            ]
        )
        await db.commit()

    resp = client.get("/api/v1/stats/trend?days=3", headers=admin_headers)
    assert resp.status_code == 200
    trend = resp.json()
    target = next(item for item in trend if item["date"] == job_day.strftime("%Y-%m-%d"))
    assert target["total"] == 10
    assert target["passed"] == 7
    assert target["pass_rate"] == 0.7
