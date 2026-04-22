from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, asc, desc
import asyncio
import logging

logger = logging.getLogger(__name__)

from database import get_db
from models.application import Application
from models.user import User
from schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut
from schemas.common import BulkDeleteResponse, BulkIdsRequest
from core.security import require_viewer, require_editor, require_admin, get_current_user
from config import settings

router = APIRouter(prefix="/applications", tags=["applications"])


def _normalize_sort_order(value: str | None) -> str:
    return "asc" if (value or "").lower() == "asc" else "desc"


def _apply_ordering(stmt, primary_column, id_column, sort_order: str):
    direction = asc if _normalize_sort_order(sort_order) == "asc" else desc
    return stmt.order_by(direction(primary_column), direction(id_column))


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _validate_docker_launch_config(app: Application) -> None:
    """Validate the final persisted Docker-compose launch configuration."""
    if (app.launch_mode or "ssh_script").lower() != "docker_compose":
        return

    missing = []
    if not app.docker_workdir:
        missing.append("docker_workdir")
    if not app.docker_service_name:
        missing.append("docker_service_name")
    if missing:
        raise HTTPException(
            status_code=422,
            detail="launch_mode=docker_compose requires: " + ", ".join(missing),
        )


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ApplicationOut])
async def list_applications(
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    sort_mapping = {
        "created_at": Application.created_at,
        "name": Application.name,
        "id": Application.id,
    }
    primary_column = sort_mapping.get(sort_by, Application.created_at)
    stmt = _apply_ordering(select(Application), primary_column, Application.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return [ApplicationOut.from_orm_with_meta(a) for a in result.scalars().all()]


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_applications(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    app_ids = sorted({app_id for app_id in body.ids if app_id})
    if not app_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(Application).where(Application.id.in_(app_ids)))
    apps = result.scalars().all()
    if not apps:
        return BulkDeleteResponse(deleted=0)

    await db.execute(delete(Application).where(Application.id.in_([item.id for item in apps])))
    await db.commit()
    return BulkDeleteResponse(deleted=len(apps))


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    data = {k: (v.strip() if isinstance(v, str) else v) for k, v in payload.model_dump().items()}
    app = Application(**data)
    db.add(app)
    await db.commit()
    await db.refresh(app)
    return ApplicationOut.from_orm_with_meta(app)


@router.get("/{app_id}", response_model=ApplicationOut)
async def get_application(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    app = await _get_app_or_404(app_id, db)
    return ApplicationOut.from_orm_with_meta(app)


@router.put("/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_editor),
):
    app = await _get_app_or_404(app_id, db)
    update_data = payload.model_dump(exclude_unset=True)
    # 密码为空字符串时不覆盖原有密码（前端留空 = 不修改密码）
    if "ssh_password" in update_data and not update_data["ssh_password"]:
        update_data.pop("ssh_password")
    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(app, field, value)
    _validate_docker_launch_config(app)
    await db.commit()
    await db.refresh(app)
    return ApplicationOut.from_orm_with_meta(app)


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
            agent_jar = settings.arex_agent_jar_path
            if (app.launch_mode or "ssh_script").lower() == "docker_compose":
                arex_url = (
                    settings.arex_agent_storage_url
                    or app.docker_storage_url
                    or app.arex_storage_url
                    or settings.docker_agent_storage_url
                )
                result = await asyncio.to_thread(
                    ssh_executor.deploy_docker_agent, app, agent_jar, arex_url
                )
            else:
                # JDK8/legacy AREX agents may need to talk to this recorder backend
                # proxy first instead of hitting arex-storage directly.
                arex_url = (
                    settings.arex_agent_storage_url
                    or app.arex_storage_url
                    or settings.arex_storage_url
                )
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

    if (app.launch_mode or "ssh_script").lower() == "docker_compose":
        result = await asyncio.to_thread(ssh_executor.remove_docker_agent, app)
        if result.startswith("ERROR:"):
            raise HTTPException(status_code=400, detail=result)
    else:
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
    if (app.launch_mode or "ssh_script").lower() == "docker_compose":
        status_info = await asyncio.to_thread(ssh_executor.get_docker_agent_status, app)
    else:
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
