import asyncio
import json
import logging
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timedelta, timezone
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, async_session_factory

logger = logging.getLogger(__name__)
DEFAULT_SECRET_KEY = "local-dev-only-change-this-secret-key"
WEAK_SECRET_KEYS = {
    DEFAULT_SECRET_KEY,
    "please-change-this-dev-only",
}


def _validate_security_config():
    if settings.secret_key not in WEAK_SECRET_KEYS:
        return
    message = (
        "AR_SECRET_KEY is still using the default development value. "
        "Set a strong random value before using this platform outside local testing."
    )
    if settings.enforce_secure_secret:
        raise RuntimeError(message)
    logger.warning(message)


def _configure_app_logging(log_file: str | None = None):
    """Configure application logging.

    Args:
        log_file: Path to the log file. If None, falls back to settings.log_file.
                  If empty string, no file handler is added.
    """
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    uvicorn_root_logger = logging.getLogger("uvicorn")
    uvicorn_logger = logging.getLogger("uvicorn.error")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    known_loggers = (
        root_logger,
        uvicorn_root_logger,
        uvicorn_logger,
        uvicorn_access_logger,
    )
    all_handlers = []
    app_handlers = []

    for known_logger in known_loggers:
        for handler in known_logger.handlers:
            if handler not in all_handlers:
                all_handlers.append(handler)
            if known_logger is not uvicorn_access_logger and handler not in app_handlers:
                app_handlers.append(handler)

    for handler in all_handlers:
        handler.setFormatter(formatter)

    # Resolve the effective log file path
    effective_log_file = log_file if log_file is not None else settings.log_file
    if effective_log_file:
        file_handler = RotatingFileHandler(
            effective_log_file,
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        if file_handler not in app_handlers:
            app_handlers.append(file_handler)

    level = uvicorn_root_logger.level if uvicorn_root_logger.level and uvicorn_root_logger.level > 0 else logging.INFO
    for logger_name in ("main", "api", "core", "database", "integration", "utils"):
        app_logger = logging.getLogger(logger_name)
        app_logger.setLevel(min(level, logging.INFO))
        if app_handlers:
            app_logger.handlers = app_handlers
            app_logger.propagate = False


async def _create_default_admin():
    """Create initial admin user on first run (no users in DB).

    Password priority:
      1. AR_ADMIN_INIT_PASSWORD env var (useful for CI / scripted deploys)
      2. Randomly generated 16-char token (printed prominently to console)
    """
    import secrets
    from sqlalchemy import select, func
    from models.user import User
    from core.security import get_password_hash

    async with async_session_factory() as db:
        count_result = await db.execute(select(func.count()).select_from(User))
        if count_result.scalar() != 0:
            return

        password = settings.admin_init_password.strip() or secrets.token_urlsafe(12)
        admin = User(
            username="admin",
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        await db.commit()

        # Print credentials to console so the operator can log in immediately.
        # Use sys.stderr so it appears even when stdout is redirected.
        import sys
        border = "=" * 60
        msg = (
            f"\n{border}\n"
            f"  FIRST RUN: initial admin account created\n"
            f"  Username : admin\n"
            f"  Password : {password}\n"
            f"  Please log in and change the password immediately.\n"
            f"  (Set AR_ADMIN_INIT_PASSWORD to skip this prompt.)\n"
            f"{border}\n"
        )
        print(msg, file=sys.stderr, flush=True)
        logger.warning("First-run admin created. See startup output for credentials.")


def _is_expected_migration_error(exc: Exception) -> bool:
    text = str(exc).lower()
    markers = (
        "duplicate column",
        "already exists",
        "column exists",
    )
    return any(marker in text for marker in markers)


async def _migrate_db():
    """Apply additive, versioned migrations for existing databases."""
    from sqlalchemy import text
    from database import engine
    from migrations import ADDITIVE_MIGRATIONS

    async with engine.begin() as conn:
        for migration_id, description, sql in ADDITIVE_MIGRATIONS:
            existing = await conn.execute(
                text("SELECT migration_id FROM schema_migration WHERE migration_id = :migration_id"),
                {"migration_id": migration_id},
            )
            if existing.first():
                continue
            try:
                await conn.execute(text(sql))
            except Exception as exc:
                if _is_expected_migration_error(exc):
                    logger.debug("Skipping already-applied migration: %s (%s)", sql, exc)
                else:
                    logger.error("Migration failed for statement: %s", sql)
                    raise
            await conn.execute(
                text(
                    "INSERT INTO schema_migration (migration_id, description) "
                    "VALUES (:migration_id, :description)"
                ),
                {"migration_id": migration_id, "description": description},
            )


async def _verify_db_schema():
    """Fail fast when an existing database is too old for the current code."""
    from sqlalchemy import inspect
    from database import engine

    required_columns = {
        "replay_job": {
            "fail_on_sub_call_diff",
            "heartbeat_at",
            "ignore_order",
            "use_sub_invocation_mocks",
            "worker_id",
        },
        "replay_result": {"actual_sub_calls", "sub_call_diff_detail", "diff_score"},
        "recording": {"sub_calls", "transaction_code", "scene_key", "dedupe_hash", "governance_status"},
    }
    required_tables = {"recording_audit_log", "replay_audit_log", "schema_migration"}

    async with engine.begin() as conn:
        def _inspect(sync_conn):
            inspector = inspect(sync_conn)
            tables = set(inspector.get_table_names())
            missing_tables = sorted(required_tables - tables)
            missing_columns = {}
            for table, columns in required_columns.items():
                if table not in tables:
                    missing_tables.append(table)
                    continue
                existing = {column["name"] for column in inspector.get_columns(table)}
                missing = sorted(columns - existing)
                if missing:
                    missing_columns[table] = missing
            return missing_tables, missing_columns

        missing_tables, missing_columns = await conn.run_sync(_inspect)

    if missing_tables or missing_columns:
        raise RuntimeError(
            "Database schema is not compatible with current code. "
            f"missing_tables={missing_tables}, missing_columns={missing_columns}"
        )


async def _backfill_arex_mocker_created_at():
    """Populate Beijing display time for legacy arex_mocker rows."""
    from sqlalchemy import select
    from models.arex_mocker import ArexMocker
    from utils.timezone import from_epoch_ms_beijing

    async with async_session_factory() as db:
        result = await db.execute(
            select(ArexMocker).where(
                ArexMocker.created_at.is_(None),
                ArexMocker.created_at_ms.is_not(None),
            )
        )
        rows = result.scalars().all()
        updated = 0
        for row in rows:
            try:
                row.created_at = from_epoch_ms_beijing(row.created_at_ms)
                updated += 1
            except Exception:
                continue

        if updated:
            await db.commit()
            logger.info("Backfilled arex_mocker.created_at for %d rows", updated)


async def _recover_stale_running_jobs(stale_after: timedelta | None = None):
    """Fail RUNNING replay jobs whose worker heartbeat is missing or stale."""
    from sqlalchemy import select
    from models.replay import ReplayJob
    from models.replay import ReplayResult
    from models.audit import ReplayAuditLog
    from utils.timezone import now_beijing

    stale_after = stale_after or timedelta(seconds=max(settings.replay_job_heartbeat_timeout_s, 1))
    now = now_beijing()
    cutoff = now - stale_after
    interrupted_statuses = {"PENDING", "RUNNING"}
    terminal_statuses = {"PASS", "FAIL", "TIMEOUT", "ERROR"}
    recovered = 0

    async with async_session_factory() as db:
        result = await db.execute(
            select(ReplayJob)
            .where(ReplayJob.status == "RUNNING")
            .where((ReplayJob.heartbeat_at.is_(None)) | (ReplayJob.heartbeat_at < cutoff))
            .order_by(ReplayJob.id)
        )
        jobs = result.scalars().all()

        for job in jobs:
            result_rows = (
                await db.execute(select(ReplayResult).where(ReplayResult.job_id == job.id))
            ).scalars().all()

            interrupted = 0
            for row in result_rows:
                if row.status in interrupted_statuses or row.status not in terminal_statuses:
                    row.status = "ERROR"
                    row.is_pass = False
                    row.failure_category = "job_interrupted"
                    row.failure_reason = "Replay worker heartbeat expired before the job completed"
                    interrupted += 1

            passed = sum(1 for row in result_rows if row.status == "PASS")
            failed = sum(1 for row in result_rows if row.status in {"FAIL", "TIMEOUT"})
            errored = sum(1 for row in result_rows if row.status not in {"PASS", "FAIL", "TIMEOUT"})

            job.status = "FAILED"
            job.total = job.total or len(result_rows)
            job.passed = passed
            job.failed = failed
            job.errored = errored
            job.finished_at = now
            job.heartbeat_at = now
            job.worker_id = None

            db.add(
                ReplayAuditLog(
                    job_id=job.id,
                    application_id=job.application_id,
                    level="ERROR",
                    event_type="job_recovered_failed",
                    message="Replay job heartbeat expired and was marked failed during startup recovery",
                    detail=json.dumps(
                        {
                            "status": "FAILED",
                            "interrupted_results": interrupted,
                            "passed": passed,
                            "failed": failed,
                            "errored": errored,
                            "heartbeat_cutoff": cutoff.isoformat(),
                        },
                        ensure_ascii=False,
                    ),
                )
            )
            recovered += 1

        if recovered:
            await db.commit()

    if recovered:
        logger.warning("Recovered %d stale RUNNING replay job(s) as FAILED", recovered)
    return recovered


async def _stale_replay_job_recovery_loop():
    interval = max(settings.replay_job_heartbeat_timeout_s / 2, 30)
    while True:
        await asyncio.sleep(interval)
        try:
            await _recover_stale_running_jobs()
        except Exception:
            logger.exception("Failed to recover stale replay jobs")


async def _cleanup_old_audit_logs(retention_days: int = 30):
    from sqlalchemy import delete
    from models.audit import RecordingAuditLog, ReplayAuditLog
    from utils.timezone import now_beijing

    cutoff = now_beijing() - timedelta(days=retention_days)
    async with async_session_factory() as db:
        replay_result = await db.execute(delete(ReplayAuditLog).where(ReplayAuditLog.created_at < cutoff))
        recording_result = await db.execute(delete(RecordingAuditLog).where(RecordingAuditLog.created_at < cutoff))
        await db.commit()
    logger.info(
        "Cleaned audit logs older than %s days: replay=%s recording=%s",
        retention_days,
        replay_result.rowcount,
        recording_result.rowcount,
    )


async def _cleanup_expired_refresh_tokens(retention_days: int | None = None):
    from sqlalchemy import delete, or_
    from models.auth import RefreshToken

    retention_days = (
        settings.refresh_token_cleanup_retention_days
        if retention_days is None
        else retention_days
    )
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=max(retention_days, 0))
    async with async_session_factory() as db:
        result = await db.execute(
            delete(RefreshToken).where(
                or_(
                    RefreshToken.expires_at < cutoff,
                    RefreshToken.revoked_at < cutoff,
                )
            )
        )
        await db.commit()
    logger.info("Cleaned expired refresh tokens: deleted=%s", result.rowcount)


async def _audit_log_cleanup_loop():
    from utils.timezone import now_beijing

    while True:
        now = now_beijing()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        await asyncio.sleep(max((next_midnight - now).total_seconds(), 60))
        try:
            await _cleanup_old_audit_logs()
        except Exception:
            logger.exception("Failed to clean old audit logs")


async def _refresh_token_cleanup_loop():
    interval = max(settings.refresh_token_cleanup_interval_hours, 1) * 3600
    while True:
        await asyncio.sleep(interval)
        try:
            await _cleanup_expired_refresh_tokens()
        except Exception:
            logger.exception("Failed to clean expired refresh tokens")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_app_logging()
    _validate_security_config()
    await init_db()
    await _migrate_db()
    await _verify_db_schema()
    await _recover_stale_running_jobs()
    await _backfill_arex_mocker_created_at()
    await _create_default_admin()
    from core.scheduler import scheduler, load_all_schedules
    await load_all_schedules()
    scheduler.start()
    audit_cleanup_task = asyncio.create_task(_audit_log_cleanup_loop())
    refresh_token_cleanup_task = asyncio.create_task(_refresh_token_cleanup_loop())
    stale_replay_job_task = asyncio.create_task(_stale_replay_job_recovery_loop())
    try:
        yield
    finally:
        audit_cleanup_task.cancel()
        refresh_token_cleanup_task.cancel()
        stale_replay_job_task.cancel()
        with suppress(asyncio.CancelledError):
            await audit_cleanup_task
        with suppress(asyncio.CancelledError):
            await refresh_token_cleanup_task
        with suppress(asyncio.CancelledError):
            await stale_replay_job_task
        scheduler.shutdown(wait=False)
        # Close all shared httpx connection-pool instances gracefully.
        from integration.arex_client import ArexClient
        await ArexClient.close_all_clients()
        from api.arex_proxy import _close_proxy_client
        await _close_proxy_client()


app = FastAPI(
    title="AREX Recorder",
    description="AREX-based traffic recording and replay management platform for Java/Spring Boot/MySQL",
    version="1.0.0",
    lifespan=lifespan,
)

_cors_origins = settings.cors_origins
_allow_credentials = True
if "*" in _cors_origins:
    # Browsers reject credentials with wildcard origins.
    # Fall back to credentialless mode and warn the operator.
    _allow_credentials = False
    logger.warning(
        "CORS: AR_CORS_ORIGINS contains '*'; allow_credentials disabled. "
        "Set explicit origins (e.g. http://localhost:5173) to enable credentials."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from core.rate_limit import limiter

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from api.v1 import auth, users, applications
from api.arex_proxy import router as arex_proxy_router
from api.v1 import sessions
from api.v1 import test_cases
from api.v1 import replays
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(applications.router, prefix="/api/v1")
app.include_router(arex_proxy_router)   # no prefix, handles /api/storage/* and /api/config/*
app.include_router(sessions.router, prefix="/api/v1")
app.include_router(test_cases.router, prefix="/api/v1")
app.include_router(replays.router, prefix="/api/v1")
from api.v1 import schedule as schedule_api
app.include_router(schedule_api.router, prefix="/api/v1")
from api.v1 import suites, ci
app.include_router(suites.router, prefix="/api/v1")
app.include_router(ci.router, prefix="/api/v1")
from api.v1 import stats as stats_api, compare as compare_api
app.include_router(stats_api.router, prefix="/api/v1")
app.include_router(compare_api.router, prefix="/api/v1")

# Initialize system plugins and refresh repository capture metadata.
from utils.system_plugin import load_plugins
from utils.repository_capture import refresh_method_metadata
load_plugins()
refresh_method_metadata()


@app.get("/api/health")
async def health():
    from sqlalchemy import text
    from integration.arex_client import ArexClient
    from database import engine

    checks = {
        "database": {"status": "unknown"},
        "arex_storage": {"status": "unknown"},
    }

    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = {"status": "ok"}
    except Exception as exc:
        checks["database"] = {"status": "error"}
        if settings.debug:
            checks["database"]["message"] = str(exc)

    try:
        async with ArexClient(settings.arex_storage_url) as client:
            reachable = await client.health_check()
        checks["arex_storage"]["status"] = "ok" if reachable else "error"
    except Exception as exc:
        checks["arex_storage"] = {"status": "error"}
        if settings.debug:
            checks["arex_storage"]["url"] = settings.arex_storage_url
            checks["arex_storage"]["message"] = str(exc)

    status = "ok" if all(item["status"] == "ok" for item in checks.values()) else "degraded"
    return {"status": status, "version": "1.0.0", "checks": checks}
