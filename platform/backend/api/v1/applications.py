from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, or_, update
import asyncio
import logging

logger = logging.getLogger(__name__)

from database import get_db
from models.application import Application
from models.arex_mocker import ArexMocker
from models.audit import RecordingAuditLog, ReplayAuditLog
from models.compare import CompareRule
from models.recording import Recording, RecordingSession
from models.replay import ReplayJob, ReplayResult
from models.suite import SuiteCase
from models.test_case import TestCase
from models.user import User
from schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationOut
from schemas.common import BulkDeleteResponse, BulkIdsRequest, PageOut
from core.security import require_viewer, require_editor, require_admin, get_current_user
from config import settings
from utils.query import apply_ordering

router = APIRouter(prefix="/applications", tags=["applications"])


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


def _diagnostic_item(
    key: str,
    label: str,
    status: str,
    message: str,
    detail: dict | None = None,
) -> dict:
    return {
        "key": key,
        "label": label,
        "status": status,
        "message": message,
        "detail": detail or {},
    }


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


async def _delete_application_graph(db: AsyncSession, app_ids: list[int]) -> int:
    """Delete applications and all rows that directly depend on them."""
    if not app_ids:
        return 0

    existing_result = await db.execute(select(Application.id).where(Application.id.in_(app_ids)))
    existing_ids = [row[0] for row in existing_result.all()]
    if not existing_ids:
        return 0

    session_result = await db.execute(
        select(RecordingSession.id).where(RecordingSession.application_id.in_(existing_ids))
    )
    session_ids = [row[0] for row in session_result.all()]

    recording_result = await db.execute(
        select(Recording.id).where(
            or_(
                Recording.application_id.in_(existing_ids),
                Recording.session_id.in_(session_ids) if session_ids else False,
            )
        )
    )
    recording_ids = [row[0] for row in recording_result.all()]

    case_result = await db.execute(select(TestCase.id).where(TestCase.application_id.in_(existing_ids)))
    case_ids = [row[0] for row in case_result.all()]

    job_result = await db.execute(select(ReplayJob.id).where(ReplayJob.application_id.in_(existing_ids)))
    job_ids = [row[0] for row in job_result.all()]

    result_conditions = []
    if job_ids:
        result_conditions.append(ReplayResult.job_id.in_(job_ids))
    if case_ids:
        result_conditions.append(ReplayResult.test_case_id.in_(case_ids))
    replay_result_ids: list[int] = []
    if result_conditions:
        result_id_result = await db.execute(select(ReplayResult.id).where(or_(*result_conditions)))
        replay_result_ids = [row[0] for row in result_id_result.all()]

    replay_audit_conditions = [ReplayAuditLog.application_id.in_(existing_ids)]
    if job_ids:
        replay_audit_conditions.append(ReplayAuditLog.job_id.in_(job_ids))
    if replay_result_ids:
        replay_audit_conditions.append(ReplayAuditLog.result_id.in_(replay_result_ids))
    if case_ids:
        replay_audit_conditions.append(ReplayAuditLog.test_case_id.in_(case_ids))
    await db.execute(delete(ReplayAuditLog).where(or_(*replay_audit_conditions)))

    recording_audit_conditions = [RecordingAuditLog.application_id.in_(existing_ids)]
    if session_ids:
        recording_audit_conditions.append(RecordingAuditLog.session_id.in_(session_ids))
    if recording_ids:
        recording_audit_conditions.append(RecordingAuditLog.recording_id.in_(recording_ids))
    await db.execute(delete(RecordingAuditLog).where(or_(*recording_audit_conditions)))

    if replay_result_ids:
        await db.execute(delete(ReplayResult).where(ReplayResult.id.in_(replay_result_ids)))
    if job_ids:
        await db.execute(delete(ReplayJob).where(ReplayJob.id.in_(job_ids)))

    if case_ids:
        await db.execute(delete(SuiteCase).where(SuiteCase.test_case_id.in_(case_ids)))
        await db.execute(delete(TestCase).where(TestCase.id.in_(case_ids)))

    if recording_ids:
        await db.execute(
            update(TestCase).where(TestCase.source_recording_id.in_(recording_ids)).values(source_recording_id=None)
        )
        await db.execute(delete(Recording).where(Recording.id.in_(recording_ids)))
    if session_ids:
        await db.execute(delete(RecordingSession).where(RecordingSession.id.in_(session_ids)))

    await db.execute(delete(CompareRule).where(CompareRule.application_id.in_(existing_ids)))
    await db.execute(delete(Application).where(Application.id.in_(existing_ids)))
    return len(existing_ids)


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.get("", response_model=PageOut[ApplicationOut] | list[ApplicationOut])
async def list_applications(
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    sort_mapping = {
        "created_at": Application.created_at,
        "name": Application.name,
        "id": Application.id,
    }
    primary_column = sort_mapping.get(sort_by, Application.created_at)
    base_stmt = select(Application)
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(base_stmt.subquery()))
        total = total_result.scalar_one()
    stmt = apply_ordering(base_stmt, primary_column, Application.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = [ApplicationOut.from_orm_with_meta(a) for a in result.scalars().all()]
    if include_total:
        return PageOut[ApplicationOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_applications(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    app_ids = sorted({app_id for app_id in body.ids if app_id})
    if not app_ids:
        return BulkDeleteResponse(deleted=0)

    deleted = await _delete_application_graph(db, app_ids)
    await db.commit()
    return BulkDeleteResponse(deleted=deleted)


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
    deleted = await _delete_application_graph(db, [app_id])
    if not deleted:
        raise HTTPException(status_code=404, detail="Application not found")
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


@router.get("/{app_id}/diagnostics")
async def application_diagnostics(
    app_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_viewer),
):
    app = await _get_app_or_404(app_id, db)
    app_identifier = app.arex_app_id or app.name
    storage_url = app.arex_storage_url or settings.arex_storage_url

    recording_count = (
        await db.execute(select(func.count(Recording.id)).where(Recording.application_id == app.id))
    ).scalar_one()
    session_count = (
        await db.execute(select(func.count(RecordingSession.id)).where(RecordingSession.application_id == app.id))
    ).scalar_one()
    mocker_count = (
        await db.execute(select(func.count(ArexMocker.id)).where(ArexMocker.app_id == app_identifier))
    ).scalar_one()
    servlet_count = (
        await db.execute(
            select(func.count(ArexMocker.id)).where(
                ArexMocker.app_id == app_identifier,
                ArexMocker.category_name == "Servlet",
            )
        )
    ).scalar_one()
    sub_call_count = (
        await db.execute(
            select(func.count(ArexMocker.id)).where(
                ArexMocker.app_id == app_identifier,
                ArexMocker.category_name != "Servlet",
            )
        )
    ).scalar_one()

    latest_recording = (
        await db.execute(
            select(Recording.recorded_at)
            .where(Recording.application_id == app.id)
            .order_by(Recording.recorded_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    latest_mocker = (
        await db.execute(
            select(ArexMocker.created_at)
            .where(ArexMocker.app_id == app_identifier)
            .order_by(ArexMocker.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    items = [
        _diagnostic_item(
            "storage_url",
            "AREX Storage 配置",
            "pass" if storage_url else "fail",
            storage_url or "未配置 AREX Storage 地址",
            {"storage_url": storage_url},
        ),
        _diagnostic_item(
            "app_id",
            "AREX App ID",
            "pass" if app_identifier else "fail",
            app_identifier or "未配置应用标识",
            {"app_id": app_identifier},
        ),
        _diagnostic_item(
            "agent_status",
            "Agent 状态",
            "pass" if app.agent_status == "online" else "warning",
            f"当前状态：{app.agent_status}",
            {"agent_status": app.agent_status},
        ),
        _diagnostic_item(
            "sessions",
            "录制会话",
            "pass" if session_count > 0 else "warning",
            f"已有 {session_count} 个录制会话",
            {"count": session_count},
        ),
        _diagnostic_item(
            "recordings",
            "平台录制入库",
            "pass" if recording_count > 0 else "warning",
            f"已入库 {recording_count} 条录制",
            {"count": recording_count, "latest_recorded_at": latest_recording.isoformat() if latest_recording else None},
        ),
        _diagnostic_item(
            "agent_upload",
            "Agent 原始上报",
            "pass" if mocker_count > 0 else "warning",
            f"已接收 {mocker_count} 条原始 mocker",
            {"count": mocker_count, "latest_mocker_at": latest_mocker.isoformat() if latest_mocker else None},
        ),
        _diagnostic_item(
            "servlet_entry",
            "入口请求捕获",
            "pass" if servlet_count > 0 else "warning",
            f"Servlet 入口记录 {servlet_count} 条",
            {"count": servlet_count},
        ),
        _diagnostic_item(
            "sub_calls",
            "子调用捕获",
            "pass" if sub_call_count > 0 else "warning",
            f"子调用 mocker {sub_call_count} 条",
            {"count": sub_call_count},
        ),
    ]
    failed = sum(1 for item in items if item["status"] == "fail")
    warnings = sum(1 for item in items if item["status"] == "warning")
    overall = "fail" if failed else "warning" if warnings else "pass"
    return {
        "application_id": app.id,
        "application_name": app.name,
        "overall_status": overall,
        "pass_count": sum(1 for item in items if item["status"] == "pass"),
        "warning_count": warnings,
        "fail_count": failed,
        "items": items,
    }
