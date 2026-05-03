"""Recording serialisation and grouping utilities.

Extracted from api/v1/sessions.py. These functions handle converting
Recording ORM objects into API response shapes and grouping logic.
"""

import logging
from datetime import datetime

from config import settings
from database import async_session_factory
from models.recording import Recording, RecordingSession
from schemas.recording import RecordingOut, RecordingGroupOut
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.timezone import BEIJING_TZ, ensure_beijing_datetime, now_beijing

logger = logging.getLogger(__name__)

# Priority for picking the "representative" recording in a group.
REPRESENTATIVE_PRIORITY: dict[str, int] = {
    "approved": 4,
    "candidate": 3,
    "raw": 2,
    "archived": 1,
    "rejected": 0,
}


async def _duplicate_count_map(db: AsyncSession, recordings: list[Recording]) -> dict[str, int]:
    hashes = {item.dedupe_hash for item in recordings if item.dedupe_hash}
    if not hashes:
        return {}
    result = await db.execute(
        select(Recording.dedupe_hash, func.count(Recording.id))
        .where(Recording.dedupe_hash.in_(hashes))
        .group_by(Recording.dedupe_hash)
    )
    return {dedupe_hash: count for dedupe_hash, count in result.all() if dedupe_hash}


def _parse_sub_call_list(value) -> list:
    if value in (None, "", []):
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        nested = (
            value.get("items")
            or value.get("subCalls")
            or value.get("sub_invocations")
            or value.get("subInvocations")
        )
        return nested if isinstance(nested, list) else [value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except Exception:
            return []
        return _parse_sub_call_list(parsed)
    return []


def _recording_quality(recording: Recording, duplicate_count: int) -> dict:
    """Compute a non-persistent quality score for recording governance."""
    score = 100
    reasons: list[str] = []

    if not recording.transaction_code:
        score -= 20
        reasons.append("未识别交易码")
    if recording.response_status is None:
        score -= 25
        reasons.append("缺少响应状态码")
    elif recording.response_status >= 500:
        score -= 25
        reasons.append(f"服务端异常响应 {recording.response_status}")
    elif recording.response_status >= 400:
        score -= 15
        reasons.append(f"客户端异常响应 {recording.response_status}")

    if not (recording.response_body or "").strip():
        score -= 15
        reasons.append("缺少响应体")

    sub_call_count = len(_parse_sub_call_list(recording.sub_calls))
    if sub_call_count == 0:
        score -= 10
        reasons.append("未捕获子调用")

    if duplicate_count > 1:
        score -= min(20, 5 + duplicate_count * 3)
        reasons.append(f"存在 {duplicate_count} 条重复样本")

    uri = (recording.request_uri or "").lower()
    if any(marker in uri for marker in ("/actuator", "/health", "/metrics", "/favicon", "/swagger", "/v3/api-docs")):
        score -= 25
        reasons.append("疑似健康检查或内部接口")

    score = max(0, min(score, 100))
    if score >= 80:
        level = "good"
        recommendation = "approve"
        if not reasons:
            reasons.append("样本完整度较高")
    elif score >= 55:
        level = "warning"
        recommendation = "candidate"
    else:
        level = "bad"
        recommendation = "reject"

    return {
        "quality_score": score,
        "quality_level": level,
        "quality_recommendation": recommendation,
        "quality_reasons": reasons,
    }


async def _serialize_recordings(db: AsyncSession, recordings: list[Recording]) -> list[RecordingOut]:
    duplicate_counts = await _duplicate_count_map(db, recordings)
    items: list[RecordingOut] = []
    for recording in recordings:
        duplicate_count = duplicate_counts.get(recording.dedupe_hash or "", 1)
        items.append(
            RecordingOut.model_validate(recording).model_copy(
                update={
                    "duplicate_count": duplicate_count,
                    **_recording_quality(recording, duplicate_count),
                }
            )
        )
    return items


def _representative_sort_key(recording: Recording) -> tuple[int, datetime, int]:
    recorded_at = recording.recorded_at or datetime.min.replace(tzinfo=BEIJING_TZ)
    return (
        REPRESENTATIVE_PRIORITY.get(recording.governance_status or "raw", 0),
        recorded_at,
        recording.id,
    )


def _group_recordings(recordings: list[Recording]) -> list[RecordingGroupOut]:
    groups: dict[tuple[int, str | None, str | None], list[Recording]] = {}
    for recording in recordings:
        key = (recording.application_id, recording.transaction_code, recording.scene_key)
        groups.setdefault(key, []).append(recording)

    result: list[RecordingGroupOut] = []
    for (application_id, transaction_code, scene_key), items in groups.items():
        representative = max(items, key=_representative_sort_key)
        latest = max(item.recorded_at for item in items)
        result.append(
            RecordingGroupOut(
                application_id=application_id,
                transaction_code=transaction_code,
                scene_key=scene_key,
                total_count=len(items),
                approved_count=sum(1 for item in items if item.governance_status == "approved"),
                candidate_count=sum(1 for item in items if item.governance_status == "candidate"),
                raw_count=sum(1 for item in items if item.governance_status == "raw"),
                latest_recorded_at=latest,
                representative_recording_id=representative.id,
                representative_governance_status=representative.governance_status,
                representative_request_method=representative.request_method,
                representative_request_uri=representative.request_uri,
            )
        )
    result.sort(key=lambda item: (item.latest_recorded_at, item.transaction_code or "", item.scene_key or ""), reverse=True)
    return result


async def _refresh_session_total_counts(db: AsyncSession, session_ids: list[int]) -> None:
    unique_ids = sorted({sid for sid in session_ids if sid})
    for session_id in unique_ids:
        count_result = await db.execute(
            select(func.count()).select_from(Recording).where(Recording.session_id == session_id)
        )
        await db.execute(
            update(RecordingSession)
            .where(RecordingSession.id == session_id)
            .values(total_count=count_result.scalar_one())
        )
