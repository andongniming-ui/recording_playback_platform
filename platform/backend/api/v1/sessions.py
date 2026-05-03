"""Recording session management & arex-storage sync."""
import asyncio
import json
import logging
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, delete, or_, desc
from sqlalchemy.exc import IntegrityError

from database import get_db, async_session_factory
from models.recording import RecordingSession, Recording
from models.application import Application
from models.arex_mocker import ArexMocker
from models.audit import RecordingAuditLog
from schemas.recording import (
    RecordingSessionCreate,
    RecordingAuditOut,
    RecordingSessionOut,
    RecordingSessionPageOut,
    RecordingOut,
    RecordingGroupOut,
    RecordingGroupPageOut,
    RecordingGovernanceUpdate,
    SyncRequest,
)
from schemas.common import BulkDeleteResponse, BulkIdsRequest, PageOut
from core.security import require_viewer, require_editor
from config import settings
from utils.governance import (
    build_dedupe_hash,
    build_scene_key,
    infer_transaction_code,
    normalize_governance_status,
    normalize_transaction_code_keys,
)
from utils.repository_capture import (
    NOISE_DYNAMIC_CLASS_OPERATIONS,
    is_noise_dynamic_mocker,
    normalize_generic_database_sub_call,
    normalize_repository_sub_call,
)
from utils.timezone import BEIJING_TZ, ensure_beijing_datetime, from_epoch_ms_beijing, now_beijing
from utils.query import apply_ordering, normalize_sort_order
from utils.serialization import json_text
from utils.arex_recording_parser import (
    _extract_records_from_query_response,
    _extract_request_body,
    _extract_request_headers,
    _extract_request_meta,
    _extract_response_body,
    _is_probable_internal_servlet_record,
)
from utils.system_plugin import get_plugin_for_app_id
from utils.dynamic_sub_calls import fetch_dynamic_class_sub_calls
from utils.dynamic_sub_calls import _fetch_dynamic_class_sub_calls
from utils.sub_call_merge import merge_sub_calls, exclude_duplicate_database_sub_calls
from utils.sub_call_parser import (
    _stringify_sub_call_value,
    _normalize_recording_filter_prefixes,
    _matches_recording_filter,
    _extract_sub_call_scalar,
    _extract_sub_call_children,
    _normalize_sub_call_item,
    _extract_sub_calls,
    _is_noise_sub_call,
    _filter_noise_sub_calls,
)
from utils.recording_serialize import (
    _duplicate_count_map,
    _parse_sub_call_list,
    _recording_quality,
    _serialize_recordings,
    _representative_sort_key,
    _group_recordings,
    _refresh_session_total_counts,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])
REPRESENTATIVE_PRIORITY = {"approved": 4, "candidate": 3, "raw": 2, "archived": 1, "rejected": 0}
_collection_tasks: set[asyncio.Task] = set()
_active_preview_locks: dict[int, asyncio.Lock] = {}
_ACTIVE_PREVIEW_LOOKBACK = timedelta(minutes=5)
_ACTIVE_PREVIEW_PAGE_SIZE = 200


def _get_active_preview_lock(session_id: int) -> asyncio.Lock:
    lock = _active_preview_locks.get(session_id)
    if lock is None:
        lock = asyncio.Lock()
        _active_preview_locks[session_id] = lock
    return lock


def _append_recording_audit(
    db: AsyncSession,
    *,
    session_id: int,
    application_id: int | None = None,
    recording_id: int | None = None,
    level: str = "INFO",
    event_type: str,
    record_id: str | None = None,
    request_method: str | None = None,
    request_uri: str | None = None,
    transaction_code: str | None = None,
    message: str | None = None,
    detail=None,
) -> None:
    db.add(
        RecordingAuditLog(
            session_id=session_id,
            application_id=application_id,
            recording_id=recording_id,
            level=level,
            event_type=event_type,
            record_id=record_id,
            request_method=request_method,
            request_uri=request_uri,
            transaction_code=transaction_code,
            message=message,
            detail=json_text(detail),
        )
    )


def _ensure_local_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _track_collection_task(task: asyncio.Task) -> None:
    _collection_tasks.add(task)

    def _cleanup(done_task: asyncio.Task) -> None:
        _collection_tasks.discard(done_task)
        try:
            done_task.result()
        except asyncio.CancelledError:
            logger.info("录制同步任务已取消")
        except Exception:
            logger.exception("录制同步任务异常退出")

    task.add_done_callback(_cleanup)


async def _count_visible_recordings_from_arex(
    client,
    *,
    app_id: str,
    begin_time: datetime,
    end_time: datetime,
    recording_filter_prefixes: list[str] | None = None,
    transaction_code_fields: list[str] | None = None,
    page_size: int = 200,
) -> int:
    """Count recordings with the same visible-entry policy used by the list view."""
    remote_total = None
    try:
        remote_total = await client.count_recordings(
            app_id=app_id,
            begin_time=begin_time,
            end_time=end_time,
        )
    except Exception as exc:
        logger.info("AREX 原始录制总数获取失败，回退到逐页计数: %s", exc)

    total = 0
    page_index = 0
    saw_records = False
    while True:
        try:
            data = await client.query_recordings(
                app_id=app_id,
                begin_time=begin_time,
                end_time=end_time,
                page_size=page_size,
                page_index=page_index,
            )
        except Exception:
            if remote_total is not None:
                return remote_total
            raise
        records = _extract_records_from_query_response(data)
        if not records:
            break
        saw_records = True
        for record in records:
            if _is_probable_internal_servlet_record(record):
                continue
            if recording_filter_prefixes:
                request_method, request_uri = _extract_request_meta(record, record)
                request_body = _extract_request_body(record)
                response_body = _extract_response_body(record)
                transaction_code = infer_transaction_code(
                    request_uri,
                    request_body,
                    response_body,
                    candidate_keys=transaction_code_fields,
                )
                if not _matches_recording_filter(transaction_code, recording_filter_prefixes):
                    continue
            total += 1
        page_index += 1
        if remote_total is not None and page_index * page_size >= remote_total:
            break
        if len(records) < page_size:
            break
    if not saw_records and remote_total is not None:
        return remote_total
    return total


async def _get_app_or_404(app_id: int, db: AsyncSession) -> Application:
    result = await db.execute(select(Application).where(Application.id == app_id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app


async def _load_session_or_404(session_id: int, db: AsyncSession) -> RecordingSession:
    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess


async def _enqueue_collection(
    session_id: int,
    sess: RecordingSession,
    body: SyncRequest,
    db: AsyncSession,
):
    recording_filter_prefixes = _normalize_recording_filter_prefixes(sess.recording_filter_prefixes)
    now = now_beijing()
    begin_time = ensure_beijing_datetime(body.begin_time or sess.start_time)
    end_time = ensure_beijing_datetime(body.end_time or now)
    sess.status = "collecting"
    sess.end_time = None
    sess.error_message = None
    _append_recording_audit(
        db,
        session_id=session_id,
        application_id=sess.application_id,
        event_type="collection_enqueued",
        message="录制同步任务已入队",
        detail={
            "begin_time": begin_time.isoformat() if begin_time else None,
            "end_time": end_time.isoformat() if end_time else None,
            "page_size": body.page_size,
            "page_index": body.page_index,
            "recording_filter_prefixes": recording_filter_prefixes,
        },
    )
    await db.commit()

    task = asyncio.create_task(
        _sync_from_arex_storage(
            session_id=session_id,
            application_id=sess.application_id,
            recording_filter_prefixes=recording_filter_prefixes,
            begin_time=begin_time,
            end_time=end_time,
            page_size=body.page_size,
            page_index=body.page_index,
        ),
        name=f"recording-sync-{session_id}",
    )
    _track_collection_task(task)
    return {"message": "Collection started", "session_id": session_id, "status": "collecting"}


async def _sync_from_arex_storage(
    session_id: int,
    application_id: int,
    recording_filter_prefixes: list[str] | None = None,
    begin_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page_size: int = 50,
    page_index: int = 0,
    finalize_session: bool = True,
    write_audit: bool = True,
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
        transaction_code_fields = normalize_transaction_code_keys(app.transaction_code_fields)
        client = ArexClient(arex_url)
        await client.__aenter__()

        # Default time range: last 7 days
        now = now_beijing()
        if not begin_time:
            from datetime import timedelta
            begin_time = now - timedelta(days=7)
        if not end_time:
            end_time = now
        begin_time = ensure_beijing_datetime(begin_time) or begin_time
        end_time = ensure_beijing_datetime(end_time) or end_time

        try:
            if write_audit:
                _append_recording_audit(
                    db,
                    session_id=session_id,
                    application_id=application_id,
                    event_type="sync_started",
                    message="开始从 AREX 拉取录制数据",
                    detail={
                        "app_id": app_id,
                        "begin_time": begin_time.isoformat() if begin_time else None,
                        "end_time": end_time.isoformat() if end_time else None,
                        "page_size": page_size,
                        "page_index": page_index,
                        "finalize_session": finalize_session,
                        "recording_filter_prefixes": recording_filter_prefixes or [],
                    },
                )
                await db.commit()
            remote_total = None
            try:
                remote_total = await client.count_recordings(
                    app_id=app_id,
                    begin_time=begin_time,
                    end_time=end_time,
                )
            except Exception as exc:
                logger.info("同步会话 %s：获取录制总数失败，回退到逐页探测: %s", session_id, exc)

            current_page = max(page_index, 0)
            while True:
                data = await client.query_recordings(
                    app_id=app_id,
                    begin_time=begin_time,
                    end_time=end_time,
                    page_size=page_size,
                    page_index=current_page,
                )
                logger.info(
                    "同步会话 %s：第 %d 页 replayCase 响应 keys: %s",
                    session_id,
                    current_page,
                    list(data.keys()) if isinstance(data, dict) else type(data).__name__,
                )
                records_raw = _extract_records_from_query_response(data)
                logger.info(
                    "同步会话 %s：第 %d 页获取到 %d 条录制记录",
                    session_id,
                    current_page,
                    len(records_raw),
                )
                if write_audit:
                    _append_recording_audit(
                        db,
                        session_id=session_id,
                        application_id=application_id,
                        event_type="page_fetched",
                        message=f"第 {current_page} 页已拉取",
                        detail={
                            "page_index": current_page,
                            "page_size": page_size,
                            "fetched_count": len(records_raw),
                            "remote_total": remote_total,
                        },
                    )
                if not records_raw:
                    if write_audit:
                        await db.commit()
                    break

                for raw in records_raw:
                    record_id = raw.get("recordId") or raw.get("id")
                    if not record_id:
                        continue
                    if _is_probable_internal_servlet_record(raw):
                        if write_audit:
                            _, skipped_uri = _extract_request_meta(raw, raw)
                            _append_recording_audit(
                                db,
                                session_id=session_id,
                                application_id=application_id,
                                event_type="record_skipped_internal",
                                record_id=str(record_id),
                                request_uri=skipped_uri,
                                message="跳过内部 Servlet 子调用录制",
                            )
                        continue

                    existing = await db.execute(
                        select(Recording).where(Recording.record_id == str(record_id))
                    )
                    if existing.scalar_one_or_none():
                        logger.debug(
                            "同步会话 %s：跳过重复录制 record_id=%s（已存在）",
                            session_id, record_id,
                        )
                        if write_audit:
                            _append_recording_audit(
                                db,
                                session_id=session_id,
                                application_id=application_id,
                                event_type="record_skipped_duplicate",
                                record_id=str(record_id),
                                message="跳过已存在的录制",
                            )
                        continue

                    try:
                        detail = await client.view_recording(str(record_id))
                    except Exception:
                        detail = raw

                    request_method, request_uri = _extract_request_meta(detail, raw)
                    request_body = _extract_request_body(detail)
                    response_body = _extract_response_body(detail)
                    response_status = detail.get("responseStatusCode") or 200
                    transaction_code = infer_transaction_code(
                        request_uri,
                        request_body,
                        response_body,
                        candidate_keys=transaction_code_fields,
                    )
                    if recording_filter_prefixes and not _matches_recording_filter(transaction_code, recording_filter_prefixes):
                        logger.info(
                            "同步会话 %s：跳过录制 %s，因为交易码 %s 不匹配过滤规则 %s",
                            session_id,
                            record_id,
                            transaction_code,
                            recording_filter_prefixes,
                        )
                        if write_audit:
                            _append_recording_audit(
                                db,
                                session_id=session_id,
                                application_id=application_id,
                                event_type="record_skipped_filter",
                                record_id=str(record_id),
                                request_method=request_method,
                                request_uri=request_uri,
                                transaction_code=transaction_code,
                                message="录制不匹配过滤规则",
                                detail={"recording_filter_prefixes": recording_filter_prefixes},
                            )
                        continue

                    record_time_ms = (
                        detail.get("creationTime") or raw.get("creationTime")
                        or raw.get("recordTime") or raw.get("createTime")
                        or detail.get("recordTime") or detail.get("createTime")
                    )
                    if record_time_ms:
                        try:
                            recorded_at = from_epoch_ms_beijing(record_time_ms)
                        except (ValueError, TypeError):
                            recorded_at = now_beijing()
                    else:
                        recorded_at = now_beijing()

                    extracted_sub_calls = _extract_sub_calls(detail, raw)
                    dynamic_sub_calls = await fetch_dynamic_class_sub_calls(str(record_id), db)

                    plugin = get_plugin_for_app_id(app_id)
                    plugin_sub_calls: list[dict] = []
                    if plugin:
                        plugin_sub_calls = await plugin.fetch_extra_sub_calls(
                            request_body, app_id, str(record_id), db
                        )

                    if plugin_sub_calls:
                        dynamic_sub_calls = exclude_duplicate_database_sub_calls(
                            plugin_sub_calls, dynamic_sub_calls
                        )
                        normalized_sub_calls = merge_sub_calls(extracted_sub_calls, plugin_sub_calls)
                        normalized_sub_calls = merge_sub_calls(normalized_sub_calls, dynamic_sub_calls)
                    else:
                        normalized_sub_calls = merge_sub_calls(extracted_sub_calls, dynamic_sub_calls)

                    rec = Recording(
                        session_id=session_id,
                        application_id=application_id,
                        record_id=str(record_id),
                        request_method=request_method,
                        request_uri=request_uri,
                        request_headers=_extract_request_headers(detail),
                        request_body=request_body,
                        response_status=response_status,
                        response_body=response_body,
                        transaction_code=transaction_code,
                        scene_key=build_scene_key(transaction_code, request_method, request_uri, response_status),
                        dedupe_hash=build_dedupe_hash(transaction_code, request_method, request_uri, request_body),
                        governance_status="raw",
                        sub_calls=json.dumps(normalized_sub_calls, ensure_ascii=False),
                        recorded_at=recorded_at,
                    )
                    try:
                        async with db.begin_nested():
                            db.add(rec)
                            await db.flush()
                    except IntegrityError:
                        logger.info(
                            "同步会话 %s：跳过并发重复录制 record_id=%s",
                            session_id,
                            record_id,
                        )
                        if write_audit:
                            _append_recording_audit(
                                db,
                                session_id=session_id,
                                application_id=application_id,
                                event_type="record_skipped_duplicate",
                                record_id=str(record_id),
                                message="跳过并发重复录制",
                            )
                        continue
                    if write_audit:
                        _append_recording_audit(
                            db,
                            session_id=session_id,
                            application_id=application_id,
                            recording_id=rec.id,
                            event_type="record_saved",
                            record_id=str(record_id),
                            request_method=request_method,
                            request_uri=request_uri,
                            transaction_code=transaction_code,
                            message="录制已入库",
                            detail={
                                "sub_call_count": len(normalized_sub_calls),
                                "response_status": response_status,
                                "recorded_at": recorded_at.isoformat() if recorded_at else None,
                            },
                        )
                    logger.info(
                        "同步会话 %s：收录 record_id=%s method=%s uri=%s transaction_code=%s sub_calls=%d",
                        session_id,
                        record_id,
                        request_method,
                        request_uri,
                        transaction_code or "-",
                        len(normalized_sub_calls),
                    )

                await db.commit()

                current_page += 1
                if remote_total is not None and current_page * page_size >= remote_total:
                    break
                if len(records_raw) < page_size:
                    break

            # Post-processing: remove sub-invocation recordings
            # (internal HTTP calls recorded as separate Servlet entry-points)
            removed = await _remove_sub_invocation_recordings(session_id, db)
            if removed:
                logger.info("同步会话 %s：移除 %d 条子调用 Servlet 录制", session_id, removed)
                if write_audit:
                    _append_recording_audit(
                        db,
                        session_id=session_id,
                        application_id=application_id,
                        event_type="sub_invocation_cleanup",
                        message="移除子调用 Servlet 录制",
                        detail={"removed_count": removed},
                    )
                    await db.commit()

            # Update session status
            sess_result = await db.execute(
                select(RecordingSession).where(RecordingSession.id == session_id)
            )
            sess = sess_result.scalar_one_or_none()
            if sess:
                count_result = await db.execute(
                    select(func.count()).select_from(Recording).where(Recording.session_id == session_id)
                )
                sess.total_count = count_result.scalar_one()
                sess.error_message = None
                if finalize_session:
                    sess.status = "done"
                    sess.end_time = end_time
                if write_audit:
                    _append_recording_audit(
                        db,
                        session_id=session_id,
                        application_id=application_id,
                        event_type="sync_finished",
                        message="录制同步完成",
                        detail={
                            "total_count": sess.total_count,
                            "finalize_session": finalize_session,
                            "status": sess.status,
                        },
                    )
                await db.commit()

        except ArexClientError as e:
            logger.error("同步会话 %s 失败: %s", session_id, e)
            if finalize_session:
                sess_result = await db.execute(
                    select(RecordingSession).where(RecordingSession.id == session_id)
                )
                sess = sess_result.scalar_one_or_none()
                if sess:
                    sess.status = "error"
                    sess.error_message = str(e)
                    _append_recording_audit(
                        db,
                        session_id=session_id,
                        application_id=application_id,
                        level="ERROR",
                        event_type="sync_failed",
                        message="AREX 同步失败",
                        detail={"error": str(e)},
                    )
                    await db.commit()
        except Exception as e:
            logger.exception("同步会话 %s 发生未预期异常: %s", session_id, e)
            if finalize_session:
                sess_result = await db.execute(
                    select(RecordingSession).where(RecordingSession.id == session_id)
                )
                sess = sess_result.scalar_one_or_none()
                if sess:
                    sess.status = "error"
                    sess.error_message = f"未预期错误: {e}"
                    _append_recording_audit(
                        db,
                        session_id=session_id,
                        application_id=application_id,
                        level="ERROR",
                        event_type="sync_failed",
                        message="录制同步发生未预期异常",
                        detail={"error": str(e)},
                    )
                    await db.commit()
        finally:
            await client.aclose()


async def _sync_active_session_preview(session_id: int, db: AsyncSession) -> None:
    lock = _get_active_preview_lock(session_id)
    if lock.locked():
        return

    async with lock:
        await _sync_active_session_preview_unlocked(session_id, db)


async def _sync_active_session_preview_unlocked(session_id: int, db: AsyncSession) -> None:
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active" or not sess.start_time:
        return

    session_start_time = _ensure_local_datetime(sess.start_time)
    if session_start_time is None:
        return

    latest_result = await db.execute(
        select(func.max(Recording.recorded_at)).where(Recording.session_id == session_id)
    )
    latest_recorded_at = _ensure_local_datetime(latest_result.scalar_one_or_none())
    begin_time = session_start_time
    if latest_recorded_at:
        begin_time = max(session_start_time, latest_recorded_at - _ACTIVE_PREVIEW_LOOKBACK)

    try:
        await _sync_from_arex_storage(
            session_id=session_id,
            application_id=sess.application_id,
            recording_filter_prefixes=_normalize_recording_filter_prefixes(sess.recording_filter_prefixes),
            begin_time=begin_time,
            end_time=now_beijing(),
            page_size=_ACTIVE_PREVIEW_PAGE_SIZE,
            page_index=0,
            finalize_session=False,
            write_audit=False,
        )
    except Exception as exc:
        logger.warning("会话 %s 预览同步失败: %s", session_id, exc)


async def _refresh_active_session_remote_counts(db: AsyncSession, sessions: list[RecordingSession]) -> None:
    """Refresh visible active sessions with a lightweight AREX count query."""
    active_sessions = [
        sess for sess in sessions
        if sess.status == "active" and sess.start_time is not None
    ]
    if not active_sessions:
        return

    from integration.arex_client import ArexClient

    app_ids = sorted({sess.application_id for sess in active_sessions})
    app_result = await db.execute(select(Application).where(Application.id.in_(app_ids)))
    app_map = {app.id: app for app in app_result.scalars().all()}
    now = now_beijing()
    changed = False

    for sess in active_sessions:
        app = app_map.get(sess.application_id)
        if not app:
            continue
        app_id = app.arex_app_id or app.name
        recording_filter_prefixes = _normalize_recording_filter_prefixes(sess.recording_filter_prefixes)
        transaction_code_fields = normalize_transaction_code_keys(app.transaction_code_fields)
        try:
            async with ArexClient(app.arex_storage_url or settings.arex_storage_url) as client:
                remote_count = await _count_visible_recordings_from_arex(
                    client,
                    app_id=app_id,
                    begin_time=ensure_beijing_datetime(sess.start_time) or sess.start_time,
                    end_time=now,
                    recording_filter_prefixes=recording_filter_prefixes,
                    transaction_code_fields=transaction_code_fields,
                )
        except Exception as exc:
            logger.info("刷新录制中会话 %s 的 AREX 计数失败: %s", sess.id, exc)
            continue
        if remote_count != sess.total_count:
            sess.total_count = remote_count
            changed = True

    if changed:
        await db.commit()


async def _remove_sub_invocation_recordings(session_id: int, db: AsyncSession) -> int:
    """移除本 session 中属于其他录制的 HTTP 子调用的 Servlet entry-point 录制。

    当 arex-agent 拦截到内部 HTTP 调用时，会将被调用方的 Servlet 请求也录制为独立
    entry-point，导致录制列表里出现主调用和子调用混合的情况。本函数通过扫描
    HttpClient 子调用 mocker 的响应头中的 arex-record-id，识别并删除这些录制。
    """
    result = await db.execute(
        select(Recording.id, Recording.record_id, Recording.request_uri, Recording.request_headers)
        .where(Recording.session_id == session_id)
    )
    rows = result.all()
    session_record_ids = {row.record_id for row in rows}
    session_id_map = {row.record_id: row.id for row in rows}
    if not session_record_ids:
        return 0

    # Scan HttpClient mockers for arex-record-id in response headers and fallback paths
    sub_invocation_record_ids: set[str] = set()
    httpclient_paths: set[str] = set()
    httpclient_result = await db.execute(
        select(ArexMocker.mocker_data).where(
            ArexMocker.record_id.in_(session_record_ids),
            ArexMocker.is_entry_point.is_(False),
            ArexMocker.category_name == "HttpClient",
        )
    )
    for mocker_json in httpclient_result.scalars().all():
        try:
            mocker = json.loads(mocker_json)
            operation_name = str(mocker.get("operationName") or "").strip()
            if operation_name:
                httpclient_paths.add(operation_name.partition("?")[0])
            target_response = mocker.get("targetResponse") or {}

            # Method 1: targetResponse.attributes.Headers (some agent versions)
            resp_attrs = target_response.get("attributes") or {}
            headers: dict = resp_attrs.get("Headers") or {}
            arex_id = headers.get("arex-record-id")

            # Method 2: targetResponse.body is a JSON string containing {"headers": {...}}
            # Used by RestTemplate instrumentation in arex-agent 0.4.x
            if not arex_id:
                resp_body = target_response.get("body")
                if isinstance(resp_body, str):
                    try:
                        parsed_body = json.loads(resp_body)
                        body_headers = parsed_body.get("headers") or {}
                        arex_id = body_headers.get("arex-record-id")
                    except Exception:
                        pass

            if isinstance(arex_id, str):
                sub_invocation_record_ids.add(arex_id)
            elif isinstance(arex_id, list):
                sub_invocation_record_ids.update(arex_id)
        except Exception:
            pass

    def _looks_like_local_internal_recording(request_uri: str | None, request_headers: str | None) -> bool:
        uri = (request_uri or "").strip()
        if uri.startswith("/internal/"):
            return True
        if not request_headers:
            return False
        try:
            headers = json.loads(request_headers) if isinstance(request_headers, str) else request_headers
        except Exception:
            return False
        if not isinstance(headers, dict):
            return False
        host = str(headers.get("host") or headers.get("Host") or "").strip().lower()
        if not (host.startswith("127.0.0.1:") or host.startswith("localhost:")):
            return False
        return uri.partition("?")[0] in httpclient_paths

    for row in rows:
        if _looks_like_local_internal_recording(row.request_uri, row.request_headers) and row.record_id:
            sub_invocation_record_ids.add(row.record_id)

    to_delete = [
        session_id_map[rid]
        for rid in sub_invocation_record_ids
        if rid in session_id_map
    ]
    if to_delete:
        await db.execute(delete(Recording).where(Recording.id.in_(to_delete)))
    return len(to_delete)


@router.get("", response_model=RecordingSessionPageOut | list[RecordingSessionOut])
async def list_sessions(
    application_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_total: bool = Query(False),
    refresh_active_count: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(RecordingSession)
    if application_id:
        stmt = stmt.where(RecordingSession.application_id == application_id)
    if status:
        stmt = stmt.where(RecordingSession.status == status)
    if search:
        stmt = stmt.join(Application, RecordingSession.application_id == Application.id).where(
            or_(
                RecordingSession.name.contains(search),
                Application.name.contains(search),
            )
        )
    if created_after:
        stmt = stmt.where(RecordingSession.created_at >= created_after)
    if created_before:
        stmt = stmt.where(RecordingSession.created_at <= created_before)
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    sort_mapping = {
        "created_at": RecordingSession.created_at,
        "start_time": RecordingSession.start_time,
        "end_time": RecordingSession.end_time,
        "total_count": RecordingSession.total_count,
        "id": RecordingSession.id,
    }
    primary_column = sort_mapping.get(sort_by, RecordingSession.created_at)
    stmt = apply_ordering(stmt, primary_column, RecordingSession.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if refresh_active_count:
        await _refresh_active_session_remote_counts(db, items)
    if include_total:
        return RecordingSessionPageOut(items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.post("", response_model=RecordingSessionOut, status_code=201)
async def create_session(
    body: RecordingSessionCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    await _get_app_or_404(body.application_id, db)
    normalized_filter_prefixes = _normalize_recording_filter_prefixes(body.recording_filter_prefixes)
    session = RecordingSession(
        application_id=body.application_id,
        name=body.name,
        status="idle",
        recording_filter_prefixes=json.dumps(normalized_filter_prefixes, ensure_ascii=False) if normalized_filter_prefixes else None,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_sessions(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    session_ids = sorted({session_id for session_id in body.ids if session_id})
    if not session_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(RecordingSession).where(RecordingSession.id.in_(session_ids)))
    sessions = result.scalars().all()
    if not sessions:
        return BulkDeleteResponse(deleted=0)

    blocked = [item.id for item in sessions if item.status in {"active", "collecting"}]
    if blocked:
        raise HTTPException(status_code=409, detail=f"Sessions are still running: {blocked[0]}")

    await db.execute(delete(Recording).where(Recording.session_id.in_([item.id for item in sessions])))
    await db.execute(delete(RecordingSession).where(RecordingSession.id.in_([item.id for item in sessions])))
    await db.commit()
    return BulkDeleteResponse(deleted=len(sessions))


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
    await _refresh_active_session_remote_counts(db, [sess])
    return sess


@router.get("/{session_id}/audit-logs", response_model=PageOut[RecordingAuditOut] | list[RecordingAuditOut])
async def list_session_audit_logs(
    session_id: int,
    event_type: Optional[str] = Query(None),
    record_id: Optional[str] = Query(None),
    transaction_code: Optional[str] = Query(None),
    recording_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    await _load_session_or_404(session_id, db)
    stmt = select(RecordingAuditLog).where(RecordingAuditLog.session_id == session_id)
    if event_type:
        stmt = stmt.where(RecordingAuditLog.event_type == event_type)
    if record_id:
        stmt = stmt.where(RecordingAuditLog.record_id == record_id)
    if transaction_code:
        stmt = stmt.where(RecordingAuditLog.transaction_code == transaction_code)
    if recording_id is not None:
        stmt = stmt.where(RecordingAuditLog.recording_id == recording_id)
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    stmt = stmt.order_by(desc(RecordingAuditLog.created_at), desc(RecordingAuditLog.id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if include_total:
        return PageOut[RecordingAuditOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


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
    if sess.status in {"active", "collecting"}:
        raise HTTPException(status_code=409, detail=f"Session is still running: {sess.status}")
    # Explicitly delete child recordings first (SQLite may not enforce FK cascade)
    await db.execute(delete(Recording).where(Recording.session_id == session_id))
    await db.delete(sess)
    await db.commit()


@router.get("/{session_id}/debug-storage")
async def debug_arex_storage(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """
    调试端点：直接查询 arex-storage 并返回原始响应。
    用于排查录制数为 0 的问题——看看 arex-storage 实际返回了什么。
    """
    from integration.arex_client import ArexClient
    from datetime import timedelta

    result = await db.execute(select(RecordingSession).where(RecordingSession.id == session_id))
    sess = result.scalar_one_or_none()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    app_result = await db.execute(select(Application).where(Application.id == sess.application_id))
    app = app_result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    arex_url = app.arex_storage_url or settings.arex_storage_url
    app_id = app.arex_app_id or app.name
    now = now_beijing()
    begin_time = now - timedelta(hours=24)

    try:
        async with ArexClient(arex_url) as client:
            raw = await client.query_recordings(
                app_id=app_id,
                begin_time=begin_time,
                end_time=now,
                page_size=50,
                page_index=0,
            )
        return {
            "arex_url": arex_url,
            "app_id": app_id,
            "begin_time": begin_time.isoformat(),
            "end_time": now.isoformat(),
            "raw_response_keys": list(raw.keys()) if isinstance(raw, dict) else str(type(raw)),
            "raw_response": raw,
        }
    except Exception as e:
        return {"error": str(e), "arex_url": arex_url, "app_id": app_id}


@router.post("/{session_id}/start")
async def start_recording(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "idle":
        raise HTTPException(status_code=409, detail=f"Session is not idle: {sess.status}")

    now = now_beijing()
    sess.status = "active"
    sess.start_time = now
    sess.end_time = None
    sess.total_count = 0
    sess.error_message = None
    _append_recording_audit(
        db,
        session_id=session_id,
        application_id=sess.application_id,
        event_type="recording_started",
        message="录制会话已启动",
        detail={"start_time": now.isoformat()},
    )
    await db.commit()
    await db.refresh(sess)
    return {"message": "Recording started", "session_id": session_id, "status": sess.status}


@router.post("/{session_id}/stop")
async def stop_recording(
    session_id: int,
    body: SyncRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Stop recording and sync buffered recordings from arex-storage."""
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active":
        raise HTTPException(status_code=409, detail=f"Session is not active: {sess.status}")
    return await _enqueue_collection(session_id, sess, body, db)


@router.post("/{session_id}/sync")
async def sync_recordings(
    session_id: int,
    body: SyncRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Compatibility alias for stop_recording."""
    sess = await _load_session_or_404(session_id, db)
    if sess.status != "active":
        raise HTTPException(status_code=409, detail=f"Session is not active: {sess.status}")
    return await _enqueue_collection(session_id, sess, body, db)


@router.get("/{session_id}/recordings", response_model=PageOut[RecordingOut] | list[RecordingOut])
async def list_recordings(
    session_id: int,
    transaction_code: Optional[str] = Query(None),
    governance_status: Optional[str] = Query(None),
    duplicate_only: bool = Query(False),
    search: Optional[str] = Query(None),
    sort_by: str = Query("recorded_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    sess = await _load_session_or_404(session_id, db)
    if sess.status == "active" and skip == 0:
        await _sync_active_session_preview(session_id, db)

    stmt = select(Recording).where(Recording.session_id == session_id)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.transaction_code.contains(search),
                Recording.tags.contains(search),
            )
        )
    if duplicate_only:
        duplicate_hashes = (
            select(Recording.dedupe_hash)
            .where(Recording.dedupe_hash.is_not(None))
            .group_by(Recording.dedupe_hash)
            .having(func.count(Recording.id) > 1)
        )
        stmt = stmt.where(Recording.dedupe_hash.in_(duplicate_hashes))
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    sort_mapping = {
        "recorded_at": Recording.recorded_at,
        "id": Recording.id,
    }
    primary_column = sort_mapping.get(sort_by, Recording.recorded_at)
    stmt = apply_ordering(stmt, primary_column, Recording.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = await _serialize_recordings(db, result.scalars().all())
    if include_total:
        return PageOut[RecordingOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.get("/recordings/all", response_model=PageOut[RecordingOut] | list[RecordingOut])
async def list_all_recordings(
    application_id: Optional[int] = Query(None),
    session_id: Optional[int] = Query(None),
    transaction_code: Optional[str] = Query(None),
    governance_status: Optional[str] = Query(None),
    duplicate_only: bool = Query(False),
    uri_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("recorded_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """List all recordings across sessions, with optional filters."""
    stmt = select(Recording)
    if application_id:
        stmt = stmt.where(Recording.application_id == application_id)
    if session_id:
        stmt = stmt.where(Recording.session_id == session_id)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if duplicate_only:
        duplicate_hashes = (
            select(Recording.dedupe_hash)
            .where(Recording.dedupe_hash.is_not(None))
            .group_by(Recording.dedupe_hash)
            .having(func.count(Recording.id) > 1)
        )
        stmt = stmt.where(Recording.dedupe_hash.in_(duplicate_hashes))
    if uri_filter:
        stmt = stmt.where(Recording.request_uri.contains(uri_filter))
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.tags.contains(search),
                Recording.transaction_code.contains(search),
            )
        )
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    sort_mapping = {
        "recorded_at": Recording.recorded_at,
        "id": Recording.id,
    }
    primary_column = sort_mapping.get(sort_by, Recording.recorded_at)
    stmt = apply_ordering(stmt, primary_column, Recording.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = await _serialize_recordings(db, result.scalars().all())
    if include_total:
        return PageOut[RecordingOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.get("/recordings/groups", response_model=RecordingGroupPageOut | list[RecordingGroupOut])
async def list_recording_groups(
    application_id: Optional[int] = Query(None),
    governance_status: Optional[str] = Query(None),
    transaction_code: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("latest_recorded_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(Recording)
    if application_id:
        stmt = stmt.where(Recording.application_id == application_id)
    if governance_status:
        stmt = stmt.where(Recording.governance_status == governance_status)
    if transaction_code:
        stmt = stmt.where(Recording.transaction_code == transaction_code)
    if search:
        stmt = stmt.where(
            or_(
                Recording.request_uri.contains(search),
                Recording.request_method.contains(search),
                Recording.transaction_code.contains(search),
                Recording.scene_key.contains(search),
                Recording.tags.contains(search),
            )
        )
    result = await db.execute(stmt.order_by(Recording.recorded_at.desc()))
    groups = _group_recordings(result.scalars().all())
    reverse = normalize_sort_order(sort_order) == "desc"
    if sort_by == "transaction_code":
        groups.sort(key=lambda item: ((item.transaction_code or "").lower(), item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    elif sort_by == "scene_key":
        groups.sort(key=lambda item: ((item.scene_key or "").lower(), item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    else:
        groups.sort(key=lambda item: (item.latest_recorded_at, item.representative_recording_id), reverse=reverse)
    if include_total:
        return RecordingGroupPageOut(items=groups[skip:skip + limit], total=len(groups), skip=skip, limit=limit)
    return groups


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
    return (await _serialize_recordings(db, [rec]))[0]


@router.post("/recordings/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_recordings(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    recording_ids = sorted({recording_id for recording_id in body.ids if recording_id})
    if not recording_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(Recording).where(Recording.id.in_(recording_ids)))
    recordings = result.scalars().all()
    if not recordings:
        return BulkDeleteResponse(deleted=0)

    session_ids = [recording.session_id for recording in recordings if recording.session_id]
    await db.execute(delete(Recording).where(Recording.id.in_([recording.id for recording in recordings])))
    await _refresh_session_total_counts(db, session_ids)
    await db.commit()
    return BulkDeleteResponse(deleted=len(recordings))


@router.delete("/recordings/{recording_id}", status_code=204)
async def delete_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Recording).where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")

    session_id = rec.session_id
    await db.delete(rec)
    if session_id:
        await _refresh_session_total_counts(db, [session_id])
    await db.commit()


@router.patch("/recordings/{recording_id}", response_model=RecordingOut)
async def update_recording_governance(
    recording_id: int,
    body: RecordingGovernanceUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Recording). where(Recording.id == recording_id))
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recording not found")

    if body.transaction_code is not None:
        rec.transaction_code = body.transaction_code.strip() or None
    elif not rec.transaction_code:
        app_result = await db.execute(select(Application).where(Application.id == rec.application_id))
        app = app_result.scalar_one_or_none()
        rec.transaction_code = infer_transaction_code(
            rec.request_body,
            rec.response_body,
            candidate_keys=normalize_transaction_code_keys(app.transaction_code_fields if app else None),
        )
    if body.governance_status is not None:
        rec.governance_status = normalize_governance_status(body.governance_status, rec.governance_status or "raw")

    rec.scene_key = build_scene_key(rec.transaction_code, rec.request_method, rec.request_uri, rec.response_status)
    rec.dedupe_hash = build_dedupe_hash(rec.transaction_code, rec.request_method, rec.request_uri, rec.request_body)
    await db.commit()
    await db.refresh(rec)
    return (await _serialize_recordings(db, [rec]))[0]
