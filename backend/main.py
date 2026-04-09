import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db, async_session_factory

logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
