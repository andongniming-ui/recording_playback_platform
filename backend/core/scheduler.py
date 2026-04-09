"""APScheduler-based async scheduler for scheduled replay tasks."""
import asyncio
import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


def _make_job_id(schedule_id: int) -> str:
    return f"schedule_{schedule_id}"


async def _run_scheduled_replay(schedule_id: int):
    """Execute a scheduled replay job."""
    from datetime import datetime, timezone
    from sqlalchemy import select
    from database import async_session_factory
    from models.schedule import Schedule
    from models.suite import Suite, SuiteCase
    from models.test_case import TestCase
    from models.replay import ReplayJob, ReplayResult
    from core.replay_executor import run_replay_job
    from utils.notify import send_replay_report

    async with async_session_factory() as db:
        result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalar_one_or_none()
        if not schedule or not schedule.is_active:
            return

        # Get case IDs from suite
        case_ids = []
        if schedule.suite_id:
            sc_result = await db.execute(
                select(SuiteCase.test_case_id)
                .where(SuiteCase.suite_id == schedule.suite_id)
                .order_by(SuiteCase.order_index)
            )
            case_ids = list(sc_result.scalars().all())

        if not case_ids:
            logger.warning(f"Schedule {schedule_id}: no cases found in suite {schedule.suite_id}")
            return

        # Create replay job
        job = ReplayJob(
            name=f"[定时] {schedule.name} - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            status="PENDING",
            concurrency=5,
            timeout_ms=5000,
            total=len(case_ids),
            diff_rules=schedule.diff_rules,
            assertions=schedule.assertions,
            perf_threshold_ms=schedule.perf_threshold_ms,
            notify_type=schedule.notify_type,
            webhook_url=schedule.notify_webhook,
        )
        db.add(job)
        await db.commit()
        await db.refresh(job)

        # Create result placeholders
        for case_id in case_ids:
            r = ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False)
            db.add(r)
        await db.commit()

        job_id = job.id
        notify_type = schedule.notify_type
        notify_webhook = schedule.notify_webhook
        schedule_name = schedule.name

        # Update last_run_at
        schedule.last_run_at = datetime.now(timezone.utc)
        schedule.last_run_status = "RUNNING"
        await db.commit()

    # Run replay (waits for completion)
    await run_replay_job(job_id)

    # Send notification
    async with async_session_factory() as db:
        from models.replay import ReplayJob
        job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
        job = job_result.scalar_one_or_none()
        if job:
            await send_replay_report(
                notify_type=notify_type,
                webhook=notify_webhook,
                job_id=job_id,
                job_name=job.name or schedule_name,
                total=job.total,
                passed=job.passed,
                failed=job.failed,
                errored=job.errored,
            )

        # Update schedule status
        sched_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        sched = sched_result.scalar_one_or_none()
        if sched:
            sched.last_run_status = "DONE" if job and job.failed == 0 else "FAILED"
            await db.commit()


def add_schedule(schedule_id: int, cron_expr: str):
    """Add or replace a scheduled job."""
    job_id = _make_job_id(schedule_id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    try:
        parts = cron_expr.strip().split()
        if len(parts) == 5:
            minute, hour, day, month, day_of_week = parts
        elif len(parts) == 6:
            second, minute, hour, day, month, day_of_week = parts
        else:
            logger.error(f"Invalid cron expression: {cron_expr}")
            return

        trigger = CronTrigger(
            minute=minute if len(parts) == 5 else minute,
            hour=hour if len(parts) == 5 else hour,
            day=day if len(parts) == 5 else day,
            month=month if len(parts) == 5 else month,
            day_of_week=day_of_week if len(parts) == 5 else day_of_week,
            timezone="Asia/Shanghai",
        )
        scheduler.add_job(
            _run_scheduled_replay,
            trigger=trigger,
            id=job_id,
            args=[schedule_id],
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=60,
        )
        logger.info(f"Scheduled job added: {job_id} cron={cron_expr}")
    except Exception as e:
        logger.error(f"Failed to add schedule {schedule_id}: {e}")


def remove_schedule(schedule_id: int):
    """Remove a scheduled job."""
    job_id = _make_job_id(schedule_id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


async def trigger_now(schedule_id: int):
    """Immediately trigger a scheduled replay (ignoring cron timing)."""
    asyncio.create_task(_run_scheduled_replay(schedule_id))


async def load_all_schedules():
    """Load all active schedules from DB on startup."""
    from sqlalchemy import select
    from database import async_session_factory
    from models.schedule import Schedule

    async with async_session_factory() as db:
        result = await db.execute(
            select(Schedule).where(Schedule.is_active == True)
        )
        schedules = result.scalars().all()
        for s in schedules:
            add_schedule(s.id, s.cron_expr)
        logger.info(f"Loaded {len(schedules)} active schedules")
