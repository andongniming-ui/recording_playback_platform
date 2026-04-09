"""Recording session management & arex-storage sync."""
import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from database import get_db, async_session_factory
from models.recording import RecordingSession, Recording
from models.application import Application
from schemas.recording import RecordingSessionCreate, RecordingSessionOut, RecordingOut, SyncRequest
from core.security import require_viewer, require_editor
from config import settings

router = APIRouter(prefix="/sessions", tags=["sessions"])


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


@router.get("", response_model=list[RecordingSessionOut])
async def list_sessions(
    application_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(RecordingSession)
    if application_id:
        stmt = stmt.where(RecordingSession.application_id == application_id)
    stmt = stmt.order_by(RecordingSession.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=RecordingSessionOut, status_code=201)
async def create_session(
    body: RecordingSessionCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    await _get_app_or_404(body.application_id, db)
    session = RecordingSession(
        application_id=body.application_id,
        name=body.name,
        status="idle",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("/{session_id}", response_model=RecordingSessionOut)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(sess)
    await db.commit()


@router.post("/{session_id}/sync")
async def sync_recordings(
    session_id: int,
    body: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Trigger a sync from arex-storage for this session's application."""
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    sess.status = "collecting"
    sess.start_time = datetime.now(timezone.utc)
    await db.commit()

    background_tasks.add_task(
        _sync_from_arex_storage,
        session_id=session_id,
        application_id=sess.application_id,
        begin_time=body.begin_time,
        end_time=body.end_time,
        page_size=body.page_size,
        page_index=body.page_index,
    )
    return {"message": "Sync started", "session_id": session_id, "status": "collecting"}


async def _sync_from_arex_storage(
    session_id: int,
    application_id: int,
    begin_time: Optional[datetime],
    end_time: Optional[datetime],
    page_size: int,
    page_index: int,
):
    """Background task: pull recordings from arex-storage and save to DB."""
    from integration.arex_client import ArexClient, ArexClientError

    async with async_session_factory() as db:
        # Get application
        result = await db.execute(select(Application).where(Application.id == application_id))
        app = result.scalar_one_or_none()
        if not app:
            return

        arex_url = app.arex_storage_url or settings.arex_storage_url
        app_id = app.arex_app_id or app.name
        client = ArexClient(arex_url)

        # Default time range: last 24 hours
        now = datetime.now(timezone.utc)
        if not begin_time:
            from datetime import timedelta
            begin_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_time:
            end_time = now

        try:
            data = await client.query_recordings(
                app_id=app_id,
                begin_time=begin_time,
                end_time=end_time,
                page_size=page_size,
                page_index=page_index,
            )
            # arex-storage response shape: {"body": [...]} or {"recordResult": [...]}
            records_raw = data.get("body") or data.get("recordResult") or []
            if isinstance(records_raw, dict):
                records_raw = records_raw.get("records") or []

            saved_count = 0
            for raw in records_raw:
                record_id = raw.get("recordId") or raw.get("id")
                if not record_id:
                    continue

                # Check if already exists
                existing = await db.execute(
                    select(Recording).where(Recording.record_id == str(record_id))
                )
                if existing.scalar_one_or_none():
                    continue

                # Try to get detail
                try:
                    detail = await client.view_recording(str(record_id))
                except Exception:
                    detail = raw

                rec = Recording(
                    session_id=session_id,
                    application_id=application_id,
                    record_id=str(record_id),
                    request_method=detail.get("operationName", "").split(" ")[0] or raw.get("operationName", "GET"),
                    request_uri=detail.get("operationName", raw.get("operationName", "/")),
                    request_headers=json.dumps(detail.get("requestHeaders") or {}),
                    request_body=json.dumps(detail.get("targetRequest") or detail.get("requestBody") or {}),
                    response_status=detail.get("responseStatusCode") or 200,
                    response_body=json.dumps(detail.get("targetResponse") or {}),
                    sub_calls=json.dumps(detail.get("subCallInfo") or []),
                    recorded_at=datetime.now(timezone.utc),
                )
                db.add(rec)
                saved_count += 1

            await db.commit()

            # Update session status
            sess_result = await db.execute(
                select(RecordingSession).where(RecordingSession.id == session_id)
            )
            sess = sess_result.scalar_one_or_none()
            if sess:
                sess.status = "done"
                sess.end_time = datetime.now(timezone.utc)
                sess.total_count = saved_count
                await db.commit()

        except ArexClientError as e:
            sess_result = await db.execute(
                select(RecordingSession).where(RecordingSession.id == session_id)
            )
            sess = sess_result.scalar_one_or_none()
            if sess:
                sess.status = "error"
                sess.error_message = str(e)
                await db.commit()


@router.get("/{session_id}/recordings", response_model=list[RecordingOut])
async def list_recordings(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = (
        select(Recording)
        .where(Recording.session_id == session_id)
        .order_by(Recording.recorded_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/recordings/all", response_model=list[RecordingOut])
async def list_all_recordings(
    application_id: Optional[int] = Query(None),
    uri_filter: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """List all recordings across sessions, with optional filters."""
    stmt = select(Recording)
    if application_id:
        stmt = stmt.where(Recording.application_id == application_id)
    if uri_filter:
        stmt = stmt.where(Recording.request_uri.contains(uri_filter))
    stmt = stmt.order_by(Recording.recorded_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/recordings/{recording_id}", response_model=RecordingOut)
async def get_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")
    return rec
