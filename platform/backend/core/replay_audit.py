"""Replay audit persistence helpers."""

import logging

import database
from models.audit import ReplayAuditLog
from utils.serialization import json_text

logger = logging.getLogger(__name__)


async def append_replay_audit_log(
    *,
    job_id: int,
    result_id: int | None = None,
    test_case_id: int | None = None,
    application_id: int | None = None,
    level: str = "INFO",
    event_type: str,
    target_url: str | None = None,
    request_method: str | None = None,
    request_uri: str | None = None,
    transaction_code: str | None = None,
    actual_status_code: int | None = None,
    latency_ms: int | None = None,
    message: str | None = None,
    detail=None,
) -> None:
    try:
        async with database.async_session_factory() as db:
            if not hasattr(db, "add"):
                return
            db.add(
                ReplayAuditLog(
                    job_id=job_id,
                    result_id=result_id,
                    test_case_id=test_case_id,
                    application_id=application_id,
                    level=level,
                    event_type=event_type,
                    target_url=target_url,
                    request_method=request_method,
                    request_uri=request_uri,
                    transaction_code=transaction_code,
                    actual_status_code=actual_status_code,
                    latency_ms=latency_ms,
                    message=message,
                    detail=json_text(detail),
                )
            )
            await db.commit()
    except Exception as exc:
        logger.warning("Failed to persist replay audit log job=%s event=%s: %s", job_id, event_type, exc)


_append_replay_audit_log = append_replay_audit_log
