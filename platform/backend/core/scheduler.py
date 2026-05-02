"""APScheduler-based async scheduler for scheduled replay tasks."""
import asyncio
import logging

from apscheduler.events import EVENT_JOB_MAX_INSTANCES, EVENT_JOB_MISSED
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from utils.timezone import now_beijing

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
_running_schedule_ids: set[int] = set()


def _log_scheduler_skip(event) -> None:
    logger.warning("Scheduled replay trigger skipped: job_id=%s code=%s", event.job_id, event.code)


scheduler.add_listener(_log_scheduler_skip, EVENT_JOB_MAX_INSTANCES | EVENT_JOB_MISSED)


def _make_job_id(schedule_id: int) -> str:
    return f"schedule_{schedule_id}"


async def _run_scheduled_replay(schedule_id: int, ignore_active: bool = False):
    """Execute a scheduled replay job."""
    import core.replay_executor as replay_executor
    from sqlalchemy import select

    from core.replay_context import infer_application_id_for_case_ids
    from database import async_session_factory
    from models.replay import ReplayJob, ReplayResult
    from models.schedule import Schedule
    from models.suite import SuiteCase
    from utils.notify import send_replay_report

    async with async_session_factory() as db:
        result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
        schedule = result.scalar_one_or_none()
        if not schedule or (not schedule.is_active and not ignore_active):
            return

        case_ids: list[int] = []
        if schedule.suite_id:
            suite_case_result = await db.execute(
                select(SuiteCase.test_case_id)
                .where(SuiteCase.suite_id == schedule.suite_id)
                .order_by(SuiteCase.order_index)
            )
            case_ids = list(suite_case_result.scalars().all())

        if not case_ids:
            schedule.last_run_at = now_beijing()
            schedule.last_run_status = "FAILED"
            await db.commit()
            logger.warning("Schedule %s: no cases found in suite %s", schedule_id, schedule.suite_id)
            return

        if schedule_id in _running_schedule_ids:
            schedule.last_run_at = now_beijing()
            schedule.last_run_status = "SKIPPED"
            await db.commit()
            logger.warning("Schedule %s skipped because previous replay is still running", schedule_id)
            return

        try:
            application_id = await infer_application_id_for_case_ids(db, case_ids)
        except ValueError as exc:
            schedule.last_run_at = now_beijing()
            schedule.last_run_status = "FAILED"
            await db.commit()
            logger.warning("Schedule %s: %s", schedule_id, exc)
            return

        if application_id is None:
            schedule.last_run_at = now_beijing()
            schedule.last_run_status = "FAILED"
            await db.commit()
            logger.warning(
                "Schedule %s: suite cases do not have application_id, cannot determine replay target",
                schedule_id,
            )
            return

        job = ReplayJob(
            name=f"[Scheduled] {schedule.name} - {now_beijing().strftime('%Y-%m-%d %H:%M')}",
            application_id=application_id,
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

        for case_id in case_ids:
            db.add(ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False))
        await db.commit()

        job_id = job.id
        notify_type = schedule.notify_type
        notify_webhook = schedule.notify_webhook
        schedule_name = schedule.name

        schedule.last_run_at = now_beijing()
        schedule.last_run_status = "RUNNING"
        await db.commit()
        _running_schedule_ids.add(schedule_id)

    async def _finish_scheduled_replay():
        try:
            await replay_executor.run_replay_job(job_id)

            async with async_session_factory() as db:
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

                schedule_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
                schedule = schedule_result.scalar_one_or_none()
                if schedule:
                    schedule.last_run_status = "DONE" if job and job.failed == 0 and job.errored == 0 else "FAILED"
                    await db.commit()
        except Exception:
            logger.exception("Scheduled replay job %s failed unexpectedly", job_id)
            async with async_session_factory() as db:
                schedule_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
                schedule = schedule_result.scalar_one_or_none()
                if schedule:
                    schedule.last_run_status = "FAILED"
                    await db.commit()
        finally:
            _running_schedule_ids.discard(schedule_id)

    asyncio.create_task(_finish_scheduled_replay())


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
            _second, minute, hour, day, month, day_of_week = parts
        else:
            logger.error("Invalid cron expression: %s", cron_expr)
            return

        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week,
            timezone="Asia/Shanghai",
        )
        scheduler.add_job(
            _run_scheduled_replay,
            trigger=trigger,
            id=job_id,
            args=[schedule_id],
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=None,
        )
        logger.info("Scheduled job added: %s cron=%s", job_id, cron_expr)
    except Exception as exc:
        logger.error("Failed to add schedule %s: %s", schedule_id, exc)


def remove_schedule(schedule_id: int):
    """Remove a scheduled job."""
    job_id = _make_job_id(schedule_id)
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)


async def trigger_now(schedule_id: int):
    """Immediately trigger a scheduled replay (ignoring cron timing)."""
    asyncio.create_task(_run_scheduled_replay(schedule_id, ignore_active=True))


async def load_all_schedules():
    """Load all active schedules from DB on startup."""
    from sqlalchemy import select

    from database import async_session_factory
    from models.schedule import Schedule

    async with async_session_factory() as db:
        result = await db.execute(select(Schedule).where(Schedule.is_active.is_(True)))
        schedules = result.scalars().all()
        for schedule in schedules:
            add_schedule(schedule.id, schedule.cron_expr)
        logger.info("Loaded %s active schedules", len(schedules))
