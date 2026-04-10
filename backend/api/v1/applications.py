from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import logging

logger = logging.getLogger(__name__)

from database import get_db
from models.application import Application
from models.user import User
from schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut
from core.security import require_viewer, require_editor, require_admin, get_current_user
from config import settings

router = APIRouter(prefix="/applications", tags=["applications"])


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ApplicationOut])
async def list_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    result = await db.execute(select(Application).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    app = Application(**payload.model_dump())
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return app


@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    return await _get_app_or_404(app_id, db)


@router.put("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    app = await _get_app_or_404(app_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(app, field, value)
    await db.commit()
    await db.refresh(app)
    return app


@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    app = await _get_app_or_404(app_id, db)
    await db.delete(app)
    await db.commit()


# ---------------------------------------------------------------------------
# SSH / Agent endpoints
# ---------------------------------------------------------------------------

@router.post("/{app_id}/test-connection")
async def test_connection(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    from integration import ssh_executor
    app = await _get_app_or_404(app_id, db)
    result = await asyncio.to_thread(ssh_executor.test_connection, app)
    return result


@router.post("/{app_id}/mount-agent")
async def mount_agent(
    app_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    app = await _get_app_or_404(app_id, db)
    app.agent_status = "mounting"
    await db.commit()

    async def _mount():
        from integration import ssh_executor
        from database import async_session_factory

        try:
            # JDK8/legacy AREX agents may need to talk to this recorder backend
            # proxy first instead of hitting arex-storage directly.
            arex_url = (
                settings.arex_agent_storage_url
                or app.arex_storage_url
                or settings.arex_storage_url
            )
            agent_jar = settings.arex_agent_jar_path
            remote_agent_path = f"/home/{app.ssh_user}/arex-agent/arex-agent.jar"

            await asyncio.to_thread(ssh_executor.upload_arex_agent, app, agent_jar)
            result = await asyncio.to_thread(
                ssh_executor.inject_javaagent_param, app, arex_url, remote_agent_path
            )
            if result.startswith("ERROR:"):
                # JDK version mismatch or other fatal configuration error
                new_status = "error"
                logger.warning("mount_agent [app=%d]: %s", app_id, result)
            elif result.startswith("OK") or result == "ALREADY_INJECTED":
                new_status = "online"
            else:
                new_status = "offline"
        except Exception as exc:
            logger.exception("mount_agent [app=%d] unexpected error: %s", app_id, exc)
            new_status = "offline"

        async with async_session_factory() as db2:
            res = await db2.execute(select(Application).where(Application.id == app_id))
            app2 = res.scalar_one_or_none()
            if app2:
                app2.agent_status = new_status
                await db2.commit()

    background_tasks.add_task(_mount)
    return {"message": "Agent mounting started", "status": "mounting"}


@router.post("/{app_id}/unmount-agent")
async def unmount_agent(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    from integration import ssh_executor
    app = await _get_app_or_404(app_id, db)

    # Remove javaagent param from start.sh via sed
    _, out1, _ = await asyncio.to_thread(
        ssh_executor.run_command,
        app,
        'find ~ -maxdepth 3 -name "start.sh" -o -name "startup.sh" 2>/dev/null | head -1',
    )
    script_path = out1.strip()
    if script_path:
        await asyncio.to_thread(
            ssh_executor.run_command,
            app,
            f"sed -i '/-javaagent/d' {script_path}",
        )

    app.agent_status = "offline"
    await db.commit()
    return {"message": "Agent unmounted", "status": "offline"}


@router.get("/{app_id}/agent-status")
async def agent_status(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    from integration import ssh_executor
    app = await _get_app_or_404(app_id, db)
    status_info = await asyncio.to_thread(ssh_executor.get_javaagent_status, app)

    # Update DB agent_status based on query result
    if status_info.get("arex_agent"):
        app.agent_status = "online"
    elif status_info.get("status") == "RUNNING":
        app.agent_status = "offline"
    else:
        app.agent_status = "offline"
    await db.commit()

    return {
        "status": app.agent_status,
        "pid": status_info.get("pid"),
        "arex_agent": status_info.get("arex_agent", False),
    }
