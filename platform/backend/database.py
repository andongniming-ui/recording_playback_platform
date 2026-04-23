from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(
    settings.db_url,
    echo=settings.debug,
    future=True,
)


@event.listens_for(engine.sync_engine, "connect")
def _configure_connection_timezone(dbapi_connection, _connection_record):
    if settings.db_type != "mysql":
        return
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SET time_zone = '+08:00'")
    finally:
        cursor.close()

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


async def init_db():
    """Create all tables. Import all models before calling create_all."""
    import models.user          # noqa: F401
    import models.application   # noqa: F401
    import models.recording     # noqa: F401
    import models.test_case     # noqa: F401
    import models.replay        # noqa: F401
    import models.compare       # noqa: F401
    import models.schedule      # noqa: F401
    import models.suite         # noqa: F401
    import models.ci            # noqa: F401
    import models.arex_mocker   # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized")
