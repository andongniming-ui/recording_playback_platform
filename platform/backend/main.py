import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, async_session_factory

logger = logging.getLogger(__name__)


def _configure_app_logging():
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

    level = uvicorn_root_logger.level if uvicorn_root_logger.level and uvicorn_root_logger.level > 0 else logging.INFO
    for logger_name in ("api", "core", "database", "integration", "utils"):
        app_logger = logging.getLogger(logger_name)
        app_logger.setLevel(min(level, logging.INFO))
        if app_handlers:
            app_logger.handlers = app_handlers
            app_logger.propagate = False


async def _create_default_admin():
    """Create default admin user if no users exist."""
    from sqlalchemy import select, func
    from models.user import User
    from core.security import get_password_hash

    async with async_session_factory() as db:
        count_result = await db.execute(select(func.count()).select_from(User))
        count = count_result.scalar()
        if count == 0:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            logger.info("Default admin user created (admin/admin123)")


async def _migrate_db():
    """为已有表追加新列（幂等：列已存在时跳过）。"""
    from sqlalchemy import text
    from database import engine

    migrations = [
        "ALTER TABLE application ADD COLUMN default_ignore_fields TEXT",
        "ALTER TABLE application ADD COLUMN default_assertions TEXT",
        "ALTER TABLE application ADD COLUMN transaction_mappings TEXT",
        "ALTER TABLE application ADD COLUMN transaction_code_fields TEXT",
        "ALTER TABLE application ADD COLUMN default_perf_threshold_ms INTEGER",
        "ALTER TABLE application ADD COLUMN launch_mode VARCHAR(32) DEFAULT 'ssh_script'",
        "ALTER TABLE application ADD COLUMN docker_workdir VARCHAR(512)",
        "ALTER TABLE application ADD COLUMN docker_compose_file VARCHAR(512)",
        "ALTER TABLE application ADD COLUMN docker_service_name VARCHAR(128)",
        "ALTER TABLE application ADD COLUMN docker_storage_url VARCHAR(512)",
        "ALTER TABLE application ADD COLUMN docker_agent_path VARCHAR(512)",
        "ALTER TABLE replay_job ADD COLUMN use_sub_invocation_mocks BOOLEAN DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN fail_on_sub_call_diff BOOLEAN DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN diff_rules TEXT",
        "ALTER TABLE replay_job ADD COLUMN assertions TEXT",
        "ALTER TABLE replay_job ADD COLUMN perf_threshold_ms INTEGER",
        "ALTER TABLE replay_job ADD COLUMN smart_noise_reduction BOOLEAN DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN retry_count INTEGER DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN ignore_fields TEXT",
        "ALTER TABLE replay_job ADD COLUMN delay_ms INTEGER DEFAULT 0",
        "ALTER TABLE replay_job ADD COLUMN repeat_count INTEGER DEFAULT 1",
        "ALTER TABLE replay_job ADD COLUMN header_transforms TEXT",
        "ALTER TABLE replay_job ADD COLUMN target_host VARCHAR(512)",
        "ALTER TABLE replay_job ADD COLUMN webhook_url VARCHAR(512)",
        "ALTER TABLE replay_job ADD COLUMN notify_type VARCHAR(32)",
        "ALTER TABLE replay_result ADD COLUMN diff_score REAL",
        "ALTER TABLE recording ADD COLUMN transaction_code VARCHAR(128)",
        "ALTER TABLE recording ADD COLUMN scene_key VARCHAR(256)",
        "ALTER TABLE recording ADD COLUMN dedupe_hash VARCHAR(64)",
        "ALTER TABLE recording ADD COLUMN governance_status VARCHAR(32) DEFAULT 'raw'",
        "ALTER TABLE arex_mocker ADD COLUMN created_at DATETIME",
        "ALTER TABLE recording_session ADD COLUMN recording_filter_prefixes TEXT",
        "ALTER TABLE test_case ADD COLUMN governance_status VARCHAR(32) DEFAULT 'candidate'",
        "ALTER TABLE test_case ADD COLUMN transaction_code VARCHAR(128)",
        "ALTER TABLE test_case ADD COLUMN scene_key VARCHAR(256)",
        "ALTER TABLE replay_suite ADD COLUMN suite_type VARCHAR(32) DEFAULT 'regression'",
        "ALTER TABLE replay_result ADD COLUMN actual_sub_calls TEXT",
    ]
    async with engine.begin() as conn:
        for sql in migrations:
            try:
                await conn.execute(text(sql))
            except Exception:
                pass  # 列已存在，忽略


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_app_logging()
    await init_db()
    await _migrate_db()
    await _backfill_arex_mocker_created_at()
    await _create_default_admin()
    from core.scheduler import scheduler, load_all_schedules
    await load_all_schedules()
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="AREX Recorder",
    description="AREX-based traffic recording and replay management platform for Java/Spring Boot/MySQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
