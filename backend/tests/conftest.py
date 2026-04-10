"""
Shared pytest fixtures for arex-recorder backend tests.

Each test gets an isolated in-memory SQLite database via the `client` fixture.
The `admin_token` and `editor_token` fixtures create users and return Bearer tokens.
"""
import sys
import os

# Ensure the backend directory is on sys.path so imports work correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, PropertyMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Core client fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client(tmp_path):
    """
    Returns a synchronous TestClient wired to a fresh per-test SQLite database.

    Isolation strategy:
    - Patch database.engine / database.async_session_factory to in-memory SQLite.
    - Override the get_db FastAPI dependency.
    - Patch APScheduler so it never actually starts across tests.
    - Patch SSH executor and ArexClient so tests don't block on real connections.
    """
    import database
    from database import get_db
    from main import app

    from sqlalchemy.pool import NullPool

    db_file = str(tmp_path / "test.db")
    db_url = f"sqlite+aiosqlite:///{db_file}"

    test_engine = create_async_engine(
        db_url,
        echo=False,
        poolclass=NullPool,
    )
    test_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Stash originals
    old_engine = database.engine
    old_factory = database.async_session_factory

    # Patch singletons used by background tasks
    database.engine = test_engine
    database.async_session_factory = test_factory

    async def _override_get_db():
        async with test_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db

    # Patch the scheduler singleton before TestClient starts (which runs lifespan)
    mock_sched = MagicMock()
    type(mock_sched).running = PropertyMock(return_value=False)
    mock_sched.start = MagicMock()
    mock_sched.shutdown = MagicMock()
    mock_sched.add_job = MagicMock()
    mock_sched.remove_job = MagicMock()
    mock_sched.get_job = MagicMock(return_value=None)

    with (
        patch("core.scheduler.scheduler", mock_sched),
        patch("api.v1.schedule.add_schedule", return_value=None),
        patch("api.v1.schedule.remove_schedule", return_value=None),
        patch("api.v1.schedule.trigger_now", new_callable=AsyncMock),
        patch("core.replay_executor.run_replay_job", new_callable=AsyncMock),
        # Patch main's local reference so lifespan _create_default_admin uses the
        # test factory (main.py imports async_session_factory by name at module level).
        patch("main.async_session_factory", test_factory),
    ):

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c

    app.dependency_overrides.clear()
    database.engine = old_engine
    database.async_session_factory = old_factory


# ---------------------------------------------------------------------------
# Token fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def admin_token(client):
    """Log in as the default admin user and return the Bearer token string."""
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def editor_token(client, admin_headers):
    """Create an editor user and return their Bearer token."""
    client.post(
        "/api/v1/users",
        json={"username": "editor1", "password": "editor123", "role": "editor"},
        headers=admin_headers,
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "editor1", "password": "editor123"},
    )
    assert resp.status_code == 200, f"Editor login failed: {resp.text}"
    return resp.json()["access_token"]


@pytest.fixture
def editor_headers(editor_token):
    return {"Authorization": f"Bearer {editor_token}"}


# ---------------------------------------------------------------------------
# Helper: create a minimal application
# ---------------------------------------------------------------------------

@pytest.fixture
def app_payload():
    """Return a minimal valid ApplicationCreate payload dict."""
    return {
        "name": "test-app",
        "ssh_host": "192.168.1.1",
        "ssh_user": "deploy",
        "ssh_port": 22,
        "service_port": 8080,
    }


@pytest.fixture
def created_app(client, admin_headers, app_payload):
    """Create an application and return its JSON."""
    resp = client.post("/api/v1/applications", json=app_payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()
