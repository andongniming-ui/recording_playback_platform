"""Replay job management API."""
import asyncio
import json
import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from sqlalchemy import String, select, or_, delete, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.replay_context import infer_application_id_for_case_ids
from core.replay_executor import register_ws, unregister_ws
from core.security import get_user_for_access_token, require_editor, require_viewer
import database
from database import get_db
from models.audit import ReplayAuditLog
from models.application import Application
from models.recording import Recording
from models.replay import ReplayJob, ReplayResult
from models.test_case import TestCase
from schemas.replay import ReplayAuditOut, ReplayJobCreate, ReplayJobOut, ReplayResultOut, ReplayRuleApplyRequest
from schemas.common import BulkDeleteResponse, BulkIdsRequest, PageOut
from utils.failure_analyzer import analyze_failure
from utils.query import apply_ordering
from utils.sub_call_matcher import (
    normalize_sub_call_type,
    normalize_http_operation,
    normalize_sub_call_operation,
    normalize_sub_call_value,
    parse_sub_call_payload,
    unwrap_sub_call_response,
)

router = APIRouter(prefix="/replays", tags=["replays"])

_DEEPDIFF_PATH_RE = re.compile(r"\['([^']+)'\]|\[(\d+)\]")


def _load_jsonish(value):
    if value in (None, ""):
        return None
    if isinstance(value, (list, dict)):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return None
    return None


def _json_list(value) -> list:
    parsed = _load_jsonish(value)
    return parsed if isinstance(parsed, list) else []


def _dump_json_list(items: list) -> str:
    return json.dumps(items, ensure_ascii=False)


def _deepdiff_path_to_dot(path: str) -> str:
    parts = []
    for key, index in _DEEPDIFF_PATH_RE.findall(path or ""):
        parts.append(key or index)
    return ".".join(parts)


def _leaf_field(path: str) -> str:
    dot_path = _deepdiff_path_to_dot(path)
    parts = [part for part in dot_path.split(".") if part and not part.isdigit()]
    return parts[-1] if parts else dot_path or path


def _suggestions_from_diff(diff_result: str | None) -> list[dict]:
    diff = _load_jsonish(diff_result)
    if not isinstance(diff, dict):
        return []

    suggestions: dict[str, dict] = {}
    for change_type, changes in diff.items():
        if not isinstance(changes, dict):
            continue
        for raw_path, detail in changes.items():
            if not isinstance(raw_path, str):
                continue
            field = _leaf_field(raw_path)
            dot_path = _deepdiff_path_to_dot(raw_path)
            if not field:
                continue
            suggestion = suggestions.setdefault(
                field,
                {
                    "key": field,
                    "field": field,
                    "path": dot_path or field,
                    "raw_path": raw_path,
                    "change_types": [],
                    "actions": ["job_ignore_fields", "application_default_ignore_fields"],
                },
            )
            if change_type not in suggestion["change_types"]:
                suggestion["change_types"].append(change_type)

            if change_type == "values_changed" and isinstance(detail, dict):
                old_value = detail.get("old_value")
                new_value = detail.get("new_value")
                if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
                    tolerance = abs(float(new_value) - float(old_value))
                    suggestion["numeric_tolerance"] = round(max(tolerance, 0.01), 6)
                    if "numeric_tolerance" not in suggestion["actions"]:
                        suggestion["actions"].append("numeric_tolerance")
                if isinstance(old_value, str) or isinstance(new_value, str):
                    if "regex_match" not in suggestion["actions"]:
                        suggestion["actions"].append("regex_match")

    return sorted(suggestions.values(), key=lambda item: item["path"])


async def _load_result_job_case_app(
    db: AsyncSession,
    result_id: int,
) -> tuple[ReplayResult, ReplayJob | None, TestCase | None, Application | None]:
    result_row = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    result = result_row.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Replay result not found")

    job = None
    if result.job_id:
        job_row = await db.execute(select(ReplayJob).where(ReplayJob.id == result.job_id))
        job = job_row.scalar_one_or_none()

    test_case = None
    if result.test_case_id:
        case_row = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
        test_case = case_row.scalar_one_or_none()

    app_id = (job.application_id if job else None) or (test_case.application_id if test_case else None)
    app = None
    if app_id:
        app_row = await db.execute(select(Application).where(Application.id == app_id))
        app = app_row.scalar_one_or_none()
    return result, job, test_case, app


def _count_sub_call_nodes(value) -> int:
    parsed = _load_jsonish(value)
    if not isinstance(parsed, list):
        return 0

    total = 0
    for item in parsed:
        if not isinstance(item, dict):
            continue
        total += 1
        for key in ("children", "subCalls", "subInvocations", "sub_invocations", "items"):
            nested = item.get(key)
            if isinstance(nested, list) and nested:
                total += _count_sub_call_nodes(nested)
                break
    return total


async def _build_result_source_context(db: AsyncSession, result: ReplayResult) -> dict:
    context = {
        "use_sub_invocation_mocks": False,
        "source_recording_id": None,
        "source_recording_transaction_code": None,
        "source_recording_scene_key": None,
        "source_recording_sub_call_count": None,
    }

    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == result.job_id))
    job = job_result.scalar_one_or_none()
    if job:
        context["use_sub_invocation_mocks"] = bool(job.use_sub_invocation_mocks)

    if not result.test_case_id:
        return context

    case_result = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
    test_case = case_result.scalar_one_or_none()
    if not test_case:
        return context

    context["source_recording_id"] = test_case.source_recording_id

    if not test_case.source_recording_id:
        return context

    rec_result = await db.execute(select(Recording).where(Recording.id == test_case.source_recording_id))
    recording = rec_result.scalar_one_or_none()
    if not recording:
        return context

    context["source_recording_transaction_code"] = recording.transaction_code
    context["source_recording_scene_key"] = recording.scene_key
    context["source_recording_sub_call_count"] = _count_sub_call_nodes(recording.sub_calls)
    return context




def _coerce_sub_call_number(value: object) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return None
    if isinstance(value, str):
        text = value.strip()
        if not re.fullmatch(r"[+-]?(?:\d+)(?:\.\d+)?", text):
            return None
        try:
            return Decimal(text)
        except (InvalidOperation, ValueError):
            return None
    return None


def _sub_call_response_equals(recorded_value: object, replayed_value: object) -> bool:
    recorded_value = unwrap_sub_call_response(recorded_value)
    replayed_value = unwrap_sub_call_response(replayed_value)

    if isinstance(recorded_value, dict) and isinstance(replayed_value, dict):
        if set(recorded_value.keys()) != set(replayed_value.keys()):
            return False
        return all(
            _sub_call_response_equals(recorded_value[key], replayed_value[key])
            for key in recorded_value
        )

    if isinstance(recorded_value, list) and isinstance(replayed_value, list):
        if len(recorded_value) != len(replayed_value):
            return False
        return all(
            _sub_call_response_equals(left, right)
            for left, right in zip(recorded_value, replayed_value)
        )

    recorded_number = _coerce_sub_call_number(recorded_value)
    replayed_number = _coerce_sub_call_number(replayed_value)
    if recorded_number is not None and replayed_number is not None:
        return recorded_number == replayed_number

    return recorded_value == replayed_value


def _sub_call_match_score(recorded_item: dict | None, replayed_item: dict | None) -> int | None:
    if not isinstance(recorded_item, dict) or not isinstance(replayed_item, dict):
        return None

    recorded_type = normalize_sub_call_type(recorded_item.get("type"))
    replayed_type = normalize_sub_call_type(replayed_item.get("type"))
    if recorded_type != replayed_type:
        return None

    recorded_operation = normalize_sub_call_operation(recorded_item)
    replayed_operation = normalize_sub_call_operation(replayed_item)
    if recorded_operation and replayed_operation:
        if recorded_operation != replayed_operation:
            return None
        recorded_request = normalize_sub_call_value(recorded_item.get("request"))
        replayed_request = normalize_sub_call_value(replayed_item.get("request"))
        if recorded_request and replayed_request and recorded_request == replayed_request:
            return 3
        return 2

    if recorded_operation or replayed_operation:
        return None

    recorded_request = normalize_sub_call_value(recorded_item.get("request"))
    replayed_request = normalize_sub_call_value(replayed_item.get("request"))
    if recorded_request and replayed_request:
        if recorded_request == replayed_request:
            return 1
        return None

    return 0


def _build_sub_call_pair(index: int, recorded_item: dict | None, replayed_item: dict | None) -> dict:
    if recorded_item and replayed_item:
        side = "both"
        try:
            response_matched = _sub_call_response_equals(
                recorded_item.get("response"),
                replayed_item.get("response"),
            )
        except Exception:
            response_matched = False
    elif recorded_item:
        side = "recorded_only"
        response_matched = None
    else:
        side = "replayed_only"
        response_matched = None

    return {
        "index": index,
        "type": (recorded_item or replayed_item or {}).get("type") or "",
        "recorded": recorded_item,
        "replayed": replayed_item,
        "side": side,
        "response_matched": response_matched,
    }


@router.post("", response_model=ReplayJobOut, status_code=201)
async def create_replay_job(
    body: ReplayJobCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Create and start a replay job."""
    if not body.case_ids:
        raise HTTPException(status_code=400, detail="case_ids must not be empty")

    from sqlalchemy import func

    count_result = await db.execute(
        select(func.count()).select_from(TestCase).where(TestCase.id.in_(body.case_ids))
    )
    found_count = count_result.scalar()
    if found_count != len(body.case_ids):
        raise HTTPException(
            status_code=400,
            detail=f"Some case_ids do not exist: expected {len(body.case_ids)}, found {found_count}",
        )

    application_id = body.application_id
    if application_id is None:
        try:
            inferred_application_id = await infer_application_id_for_case_ids(db, body.case_ids)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if inferred_application_id is not None:
            application_id = inferred_application_id

    job_name = (body.name or "").strip() or f"Replay {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    job = ReplayJob(
        name=job_name,
        application_id=application_id,
        status="PENDING",
        concurrency=body.concurrency,
        timeout_ms=body.timeout_ms,
        delay_ms=body.delay_ms,
        total=len(body.case_ids),
        use_sub_invocation_mocks=body.use_sub_invocation_mocks,
        fail_on_sub_call_diff=body.fail_on_sub_call_diff,
        ignore_fields=json.dumps(body.ignore_fields, ensure_ascii=False) if body.ignore_fields else None,
        diff_rules=json.dumps([rule.model_dump(exclude_none=True) for rule in body.diff_rules], ensure_ascii=False) if body.diff_rules else None,
        assertions=json.dumps([rule.model_dump(exclude_none=True) for rule in body.assertions], ensure_ascii=False) if body.assertions else None,
        header_transforms=json.dumps([item.model_dump(exclude_none=True) for item in body.header_transforms], ensure_ascii=False) if body.header_transforms else None,
        perf_threshold_ms=body.perf_threshold_ms,
        webhook_url=body.webhook_url,
        notify_type=body.notify_type,
        smart_noise_reduction=body.smart_noise_reduction,
        ignore_order=body.ignore_order,
        retry_count=body.retry_count,
        repeat_count=body.repeat_count,
        target_host=body.target_host,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in body.case_ids:
        db.add(
            ReplayResult(
                job_id=job.id,
                test_case_id=case_id,
                status="PENDING",
                is_pass=False,
            )
        )
    await db.commit()

    import core.replay_executor as replay_executor

    asyncio.create_task(replay_executor.run_replay_job(job.id))
    return job


@router.get("", response_model=PageOut[ReplayJobOut] | list[ReplayJobOut])
async def list_replay_jobs(
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
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(ReplayJob)
    if application_id:
        stmt = stmt.where(ReplayJob.application_id == application_id)
    if status:
        stmt = stmt.where(ReplayJob.status == status)
    if search:
        stmt = stmt.where(
            or_(
                ReplayJob.name.contains(search),
                ReplayJob.id.cast(String).contains(search),
            )
        )
    if created_after:
        stmt = stmt.where(ReplayJob.created_at >= created_after)
    if created_before:
        stmt = stmt.where(ReplayJob.created_at <= created_before)
    total = None
    include_total_enabled = include_total is True
    if include_total_enabled:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    sort_mapping = {
        "created_at": ReplayJob.created_at,
        "started_at": ReplayJob.started_at,
        "finished_at": ReplayJob.finished_at,
        "id": ReplayJob.id,
    }
    primary_column = sort_mapping.get(sort_by, ReplayJob.created_at)
    stmt = apply_ordering(stmt, primary_column, ReplayJob.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if include_total_enabled:
        return PageOut[ReplayJobOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.get("/{job_id}", response_model=ReplayJobOut)
async def get_replay_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")
    return job


@router.get("/{job_id}/audit-logs", response_model=PageOut[ReplayAuditOut] | list[ReplayAuditOut])
async def list_replay_audit_logs(
    job_id: int,
    case_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None),
    result_id: Optional[int] = Query(None),
    transaction_code: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")

    stmt = select(ReplayAuditLog).where(ReplayAuditLog.job_id == job_id)
    if case_id is not None:
        stmt = stmt.where(ReplayAuditLog.test_case_id == case_id)
    if event_type:
        stmt = stmt.where(ReplayAuditLog.event_type == event_type)
    if result_id is not None:
        stmt = stmt.where(ReplayAuditLog.result_id == result_id)
    if transaction_code:
        stmt = stmt.where(ReplayAuditLog.transaction_code == transaction_code)
    total = None
    include_total_enabled = include_total is True
    if include_total_enabled:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    stmt = stmt.order_by(desc(ReplayAuditLog.created_at), desc(ReplayAuditLog.id)).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if include_total_enabled:
        return PageOut[ReplayAuditOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_replay_jobs(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    job_ids = sorted({job_id for job_id in body.ids if job_id})
    if not job_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(ReplayJob).where(ReplayJob.id.in_(job_ids)))
    jobs = result.scalars().all()
    if not jobs:
        return BulkDeleteResponse(deleted=0)

    blocked = [job.id for job in jobs if job.status == "RUNNING"]
    if blocked:
        raise HTTPException(status_code=409, detail=f"Replay jobs are still running: {blocked[0]}")

    delete_ids = [job.id for job in jobs]
    await db.execute(delete(ReplayResult).where(ReplayResult.job_id.in_(delete_ids)))
    await db.execute(delete(ReplayJob).where(ReplayJob.id.in_(delete_ids)))
    await db.commit()
    return BulkDeleteResponse(deleted=len(delete_ids))


@router.delete("/{job_id}", status_code=204)
async def delete_replay_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")
    if job.status == "RUNNING":
        raise HTTPException(status_code=409, detail=f"Replay job is still running: {job.status}")

    await db.execute(delete(ReplayResult).where(ReplayResult.job_id == job_id))
    await db.delete(job)
    await db.commit()


@router.get("/results/{result_id}", response_model=ReplayResultOut)
async def get_replay_result(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    replay_result = result.scalar_one_or_none()
    if not replay_result:
        raise HTTPException(status_code=404, detail="Replay result not found")
    out = ReplayResultOut.model_validate(replay_result)
    tx_result = await db.execute(
        select(TestCase.transaction_code).where(TestCase.id == replay_result.test_case_id)
    )
    out.transaction_code = tx_result.scalar_one_or_none()
    context = await _build_result_source_context(db, replay_result)
    for key, value in context.items():
        setattr(out, key, value)
    return out


@router.get("/results/{result_id}/rule-suggestions")
async def get_result_rule_suggestions(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result, job, test_case, app = await _load_result_job_case_app(db, result_id)
    return {
        "result_id": result.id,
        "job_id": result.job_id,
        "application_id": app.id if app else None,
        "test_case_id": test_case.id if test_case else None,
        "suggestions": _suggestions_from_diff(result.diff_result),
        "job_ignore_fields": _json_list(job.ignore_fields if job else None),
        "application_default_ignore_fields": _json_list(app.default_ignore_fields if app else None),
    }


@router.post("/results/{result_id}/rule-suggestions/apply")
async def apply_result_rule_suggestion(
    result_id: int,
    body: ReplayRuleApplyRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result, job, _test_case, app = await _load_result_job_case_app(db, result_id)
    suggestions = _suggestions_from_diff(result.diff_result)
    suggestion = next((item for item in suggestions if item.get("key") == body.suggestion_key), None)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Rule suggestion not found")

    field = str(suggestion.get("field") or "").strip()
    if not field:
        raise HTTPException(status_code=400, detail="Rule suggestion has no field")

    if body.target == "job_ignore_fields":
        if not job:
            raise HTTPException(status_code=404, detail="Replay job not found")
        fields = _json_list(job.ignore_fields)
        if field not in fields:
            fields.append(field)
        job.ignore_fields = _dump_json_list(fields)
        await db.commit()
        return {"target": body.target, "ignore_fields": fields}

    if not app:
        raise HTTPException(status_code=404, detail="Application not found for replay result")
    fields = _json_list(app.default_ignore_fields)
    if field not in fields:
        fields.append(field)
    app.default_ignore_fields = _dump_json_list(fields)
    await db.commit()
    return {"target": body.target, "ignore_fields": fields, "application_id": app.id}


def _pair_sub_calls(recorded: list, replayed: list) -> list:
    """Pair recorded and replayed sub-calls by type/operation signature."""
    recorded_items = recorded if isinstance(recorded, list) else []
    replayed_items = replayed if isinstance(replayed, list) else []
    unmatched_replayed = set(range(len(replayed_items)))
    pairs = []
    for recorded_item in recorded_items:
        best_index = None
        best_score = None
        for replayed_index, replayed_item in enumerate(replayed_items):
            if replayed_index not in unmatched_replayed:
                continue
            score = _sub_call_match_score(recorded_item, replayed_item)
            if score is None:
                continue
            if best_score is None or score > best_score:
                best_score = score
                best_index = replayed_index
        if best_index is None:
            pairs.append(_build_sub_call_pair(len(pairs) + 1, recorded_item, None))
            continue
        unmatched_replayed.remove(best_index)
        pairs.append(_build_sub_call_pair(len(pairs) + 1, recorded_item, replayed_items[best_index]))

    for replayed_index, replayed_item in enumerate(replayed_items):
        if replayed_index in unmatched_replayed:
            pairs.append(_build_sub_call_pair(len(pairs) + 1, None, replayed_item))
    return pairs


def _build_sub_call_pair_from_detail(index: int, detail: dict) -> dict:
    detail = detail if isinstance(detail, dict) else {}
    matched = bool(detail.get("matched"))
    expected_response = detail.get("expected_response")
    actual_response = detail.get("actual_response")
    side = "both"
    if not matched:
        side = "replayed_only" if expected_response is None and actual_response is not None else "recorded_only"

    operation = detail.get("operation") or ""
    pair_type = detail.get("type") or ""
    recorded = None
    replayed = None
    if side in {"both", "recorded_only"}:
        recorded = {
            "type": pair_type,
            "operation": operation,
            "response": expected_response,
        }
    if side in {"both", "replayed_only"}:
        replayed = {
            "type": pair_type,
            "operation": operation,
            "response": actual_response,
        }

    return {
        "index": index,
        "type": pair_type,
        "recorded": recorded,
        "replayed": replayed,
        "side": side,
        "response_matched": None if side != "both" else not bool(detail.get("has_diff")),
        "has_diff": bool(detail.get("has_diff")),
        "diff_result": detail.get("diff_result"),
    }


@router.get("/results/{result_id}/sub-call-diff")
async def get_sub_call_diff(
    result_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Return paired sub-calls for a replay result: recorded vs replayed."""
    result_row = await db.execute(select(ReplayResult).where(ReplayResult.id == result_id))
    result = result_row.scalar_one_or_none()
    if not result:
        raise HTTPException(status_code=404, detail="Replay result not found")

    # Load recorded sub-calls from source recording
    recorded_raw = []
    if result.test_case_id:
        case_row = await db.execute(select(TestCase).where(TestCase.id == result.test_case_id))
        test_case = case_row.scalar_one_or_none()
        if test_case and test_case.source_recording_id:
            rec_row = await db.execute(
                select(Recording).where(Recording.id == test_case.source_recording_id)
            )
            recording = rec_row.scalar_one_or_none()
            if recording and recording.sub_calls:
                try:
                    recorded_raw = json.loads(recording.sub_calls)
                    if not isinstance(recorded_raw, list):
                        recorded_raw = []
                except Exception:
                    recorded_raw = []

    # Load replayed sub-calls stored during replay execution
    replayed_raw = []
    if result.actual_sub_calls:
        try:
            replayed_raw = json.loads(result.actual_sub_calls)
            if not isinstance(replayed_raw, list):
                replayed_raw = []
        except Exception:
            replayed_raw = []

    pairs = []
    if result.sub_call_diff_detail:
        try:
            detail_pairs = json.loads(result.sub_call_diff_detail)
            if isinstance(detail_pairs, list):
                pairs = [
                    _build_sub_call_pair_from_detail(index + 1, item)
                    for index, item in enumerate(detail_pairs)
                ]
        except Exception:
            pairs = []
    if not pairs:
        pairs = _pair_sub_calls(recorded_raw, replayed_raw)
    return {
        "recorded": recorded_raw,
        "replayed": replayed_raw,
        "pairs": pairs,
    }


@router.get("/{job_id}/results", response_model=PageOut[ReplayResultOut] | list[ReplayResultOut])
async def list_results(
    job_id: int,
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = (
        select(ReplayResult, TestCase.transaction_code)
        .outerjoin(TestCase, TestCase.id == ReplayResult.test_case_id)
        .where(ReplayResult.job_id == job_id)
    )
    if status:
        stmt = stmt.where(ReplayResult.status == status)
    total = None
    include_total_enabled = include_total is True
    if include_total_enabled:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    stmt = stmt.order_by(ReplayResult.id).offset(skip).limit(limit)
    rows = (await db.execute(stmt)).all()
    results = []
    for rr, tx_code in rows:
        out = ReplayResultOut.model_validate(rr)
        out.transaction_code = tx_code
        context = await _build_result_source_context(db, rr)
        for key, value in context.items():
            setattr(out, key, value)
        results.append(out)
    if include_total_enabled:
        return PageOut[ReplayResultOut](items=results, total=total or 0, skip=skip, limit=limit)
    return results


@router.get("/{job_id}/report")
async def get_html_report(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Generate a detailed downloadable HTML report for a replay job."""
    from fastapi.responses import Response as FastAPIResponse
    from models.application import Application

    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    results_query = await db.execute(
        select(ReplayResult).where(ReplayResult.job_id == job_id).order_by(ReplayResult.id)
    )
    results = results_query.scalars().all()

    # 获取应用名称
    app_name = "-"
    if job.application_id:
        app_res = await db.execute(select(Application).where(Application.id == job.application_id))
        app = app_res.scalar_one_or_none()
        if app:
            app_name = app.name

    # 获取测试用例 request_body / transaction_code
    case_ids = [r.test_case_id for r in results if r.test_case_id]
    case_map: dict[int, any] = {}
    if case_ids:
        cases_res = await db.execute(select(TestCase).where(TestCase.id.in_(case_ids)))
        for tc in cases_res.scalars().all():
            case_map[tc.id] = tc

    source_recording_map: dict[int, dict] = {}
    for tc in case_map.values():
        if not tc.source_recording_id or tc.source_recording_id in source_recording_map:
            continue
        rec_res = await db.execute(select(Recording).where(Recording.id == tc.source_recording_id))
        recording = rec_res.scalar_one_or_none()
        if recording:
            source_recording_map[tc.source_recording_id] = {
                "transaction_code": recording.transaction_code,
                "scene_key": recording.scene_key,
                "sub_call_count": _count_sub_call_nodes(recording.sub_calls),
            }

    import html as html_lib

    def esc(s: str) -> str:
        return html_lib.escape(str(s)) if s else ""

    pass_rate_num = (job.passed / job.total * 100) if job.total > 0 else 0
    pass_rate_str = f"{pass_rate_num:.1f}%"
    pass_color = "#18a058" if pass_rate_num >= 90 else "#f0a020" if pass_rate_num >= 60 else "#d03050"

    status_label_map = {"PENDING": "待执行", "RUNNING": "运行中", "DONE": "已完成", "FAILED": "存在失败", "CANCELLED": "已取消"}

    # 忽略字段 / 差异规则 / 断言规则
    ignore_fields_list: list[str] = []
    if job.ignore_fields:
        try:
            ignore_fields_list = json.loads(job.ignore_fields)
        except Exception:
            pass
    diff_rules_str = "无"
    if job.diff_rules:
        try:
            rules = json.loads(job.diff_rules)
            diff_rules_str = ", ".join(r.get("type", "") for r in rules) if rules else "无"
        except Exception:
            pass
    assertions_str = "无"
    if job.assertions:
        try:
            assts = json.loads(job.assertions)
            assertions_str = ", ".join(a.get("type", "") for a in assts) if assts else "无"
        except Exception:
            pass
    mock_mode_str = "开启" if job.use_sub_invocation_mocks else "关闭"

    # 失败原因分析
    from utils.failure_analyzer import analyze_failure
    category_counts: dict[str, int] = {"ENVIRONMENT": 0, "DATA_ISSUE": 0, "BUG": 0, "PERFORMANCE": 0, "UNKNOWN": 0}
    fail_results = [r for r in results if not r.is_pass]
    for rr in fail_results:
        assertion_list = None
        if rr.assertion_results:
            try:
                assertion_list = json.loads(rr.assertion_results)
            except Exception:
                pass
        category, _ = analyze_failure(
            error_message=rr.failure_reason if rr.status in ("ERROR", "TIMEOUT") else None,
            diff_json=rr.diff_result, diff_score=rr.diff_score,
            replayed_status_code=rr.actual_status_code, assertion_results=assertion_list,
        )
        if category in category_counts:
            category_counts[category] += 1

    total_fail_cnt = len(fail_results) or 1
    analysis_cells = ""
    category_defs = [
        ("ENVIRONMENT", "🌐", "环境问题", "#f0a020"),
        ("DATA_ISSUE",  "📝", "数据问题", "#2080f0"),
        ("BUG",         "🐛", "代码缺陷", "#d03050"),
        ("PERFORMANCE", "⚡", "性能问题", "#8a2be2"),
        ("UNKNOWN",     "❓", "未知",     "#999"),
    ]
    for key, icon, label, color in category_defs:
        cnt = category_counts.get(key, 0)
        pct = cnt / total_fail_cnt * 100
        analysis_cells += f"""<td class="analysis-cell">
            <div class="a-icon">{icon}</div>
            <div class="a-label">{label}</div>
            <div class="a-count" style="color:{color}">{cnt}</div>
            <div class="a-bar-bg"><div class="a-bar" style="width:{pct:.0f}%;background:{color}"></div></div>
            <div class="a-pct">{pct:.0f}%</div>
        </td>"""

    # 逐条结果
    rows_html = ""
    for i, result in enumerate(results):
        tc = case_map.get(result.test_case_id) if result.test_case_id else None
        tx_code = tc.transaction_code if tc else ""
        req_body = tc.request_body if tc else ""
        source_recording = source_recording_map.get(tc.source_recording_id) if tc and tc.source_recording_id else None

        status_cls = "pass" if result.is_pass else ("error" if result.status in ("ERROR", "TIMEOUT") else "fail")
        status_txt = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERROR", "TIMEOUT": "TIMEOUT"}.get(result.status, result.status)
        latency = f"{result.latency_ms}" if result.latency_ms is not None else "-"
        source_summary = "-"
        if source_recording:
            source_summary = f"录制 #{tc.source_recording_id} / 子调用 {source_recording['sub_call_count']}"

        # Diff score + diff count
        diff_count = 0
        diff_details_html = ""
        if result.diff_result:
            try:
                diff_obj = json.loads(result.diff_result)
                if isinstance(diff_obj, dict):
                    diff_count = len(diff_obj)
                    for path, detail in list(diff_obj.items())[:20]:
                        detail_str = json.dumps(detail, ensure_ascii=False) if not isinstance(detail, str) else detail
                        diff_details_html += f"<div class='diff-item'><span class='diff-path'>{esc(path)}</span><div class='diff-val'>{esc(detail_str)}</div></div>"
            except Exception:
                pass
        diff_score_str = f"score={result.diff_score:.3f}，{diff_count} 处差异" if result.diff_score is not None else "-"
        diff_color = "#18a058" if (result.diff_score or 0) <= 0.1 else "#f0a020" if (result.diff_score or 0) <= 0.5 else "#d03050"

        # 请求体
        req_body_disp = esc(req_body[:4000]) if req_body else "(无)"
        # 响应（原始/回放）
        expected_raw = result.expected_response or ""
        actual_raw = result.actual_response or ""
        # 不做 JSON 格式化（XML 等原样展示）
        expected_disp = esc(expected_raw[:4000])
        actual_disp = esc(actual_raw[:4000])

        detail_id = f"d{i}"
        detail_block = f"""<tr id="{detail_id}" class="detail-row" style="display:none">
  <td colspan="6">
    <div class="detail-grid">
      <div class="detail-section">
        <div class="detail-title">📤 请求体（录制时）</div>
        <pre class="code-pre">{req_body_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">🔗 来源录制</div>
        <pre class="code-pre">{esc(source_summary)}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">📥 原始响应（录制时）</div>
        <pre class="code-pre">{expected_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">🔄 回放响应</div>
        <pre class="code-pre">{actual_disp}</pre>
      </div>
      <div class="detail-section">
        <div class="detail-title">📋 差异明细</div>
        <div class="diff-details">{diff_details_html if diff_details_html else '<span style="color:#999">无差异明细</span>'}</div>
      </div>
    </div>
  </td>
</tr>"""

        click_attr = f'onclick="toggle(\'{detail_id}\')" style="cursor:pointer"'
        interface_label = f"{esc(result.request_uri or '')}"
        if tx_code:
            interface_label += f'<br><span class="tx-code">{esc(tx_code)}</span>'
        interface_label += '<br><span class="detail-hint">点击查看详情</span>'
        time_str = result.created_at.strftime("%Y-%m-%d %H:%M:%S") if result.created_at else "-"
        rows_html += f"""<tr class="result-row" data-status="{result.status}" {click_attr}>
  <td class="uri-cell">{interface_label}</td>
  <td><span class="badge {status_cls}">{status_txt}</span></td>
  <td style="color:{diff_color};font-size:12px">{esc(diff_score_str)}</td>
  <td>{result.actual_status_code or '-'}</td>
  <td>{latency}</td>
  <td class="time-cell">{time_str}</td>
</tr>{detail_block}"""

    ignore_meta = "、".join(ignore_fields_list) if ignore_fields_list else "无"
    started = job.started_at.strftime("%Y-%m-%d %H:%M:%S") if job.started_at else "-"
    ended = job.finished_at.strftime("%Y-%m-%d %H:%M:%S") if job.finished_at else "-"
    job_name = esc(job.name or f"任务 #{job_id}")
    from utils.report_templates import render_template

    html = render_template(
        "replay_report.html",
        {
            "job_name": job_name,
            "job_id": job_id,
            "app_name": esc(app_name),
            "job_status": esc(status_label_map.get(job.status, job.status)),
            "started": started,
            "ended": ended,
            "concurrency": job.concurrency,
            "timeout_ms": job.timeout_ms,
            "ignore_meta": esc(ignore_meta),
            "diff_rules": esc(diff_rules_str),
            "assertions": esc(assertions_str),
            "mock_mode": mock_mode_str,
            "total": job.total,
            "passed": job.passed,
            "failed": job.failed,
            "errored": job.errored,
            "pass_rate": pass_rate_str,
            "pass_color": pass_color,
            "analysis_cells": analysis_cells,
            "rows_html": rows_html,
        },
    )
    filename = f"replay_report_{job_id}.html"
    return FastAPIResponse(
        content=html.encode("utf-8"),
        media_type="text/html; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

@router.get("/{job_id}/analysis")
async def get_failure_analysis(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """
    对回放任务的失败结果做 5 类自动归因分析。

    返回:
        {
            "job_id": int,
            "total_failures": int,
            "categories": {
                "ENVIRONMENT": {"count": int, "percentage": float, "results": [...]},
                "DATA_ISSUE":  {"count": int, "percentage": float, "results": [...]},
                "BUG":         {"count": int, "percentage": float, "results": [...]},
                "PERFORMANCE": {"count": int, "percentage": float, "results": [...]},
                "UNKNOWN":     {"count": int, "percentage": float, "results": [...]},
            }
        }
    """
    job_result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Replay job not found")

    stmt = (
        select(ReplayResult)
        .where(ReplayResult.job_id == job_id)
        .where(ReplayResult.status.in_(["FAIL", "ERROR", "TIMEOUT"]))
        .order_by(ReplayResult.id)
    )
    fail_results = (await db.execute(stmt)).scalars().all()

    categories: dict = {
        "ENVIRONMENT": {"count": 0, "percentage": 0.0, "results": []},
        "DATA_ISSUE":  {"count": 0, "percentage": 0.0, "results": []},
        "BUG":         {"count": 0, "percentage": 0.0, "results": []},
        "PERFORMANCE": {"count": 0, "percentage": 0.0, "results": []},
        "UNKNOWN":     {"count": 0, "percentage": 0.0, "results": []},
    }

    for rr in fail_results:
        # 解析断言结果
        assertion_list = None
        if rr.assertion_results:
            try:
                assertion_list = json.loads(rr.assertion_results)
            except Exception:
                pass

        # 用 analyze_failure 重新归因（不改动已存储的 failure_category）
        category, reason = analyze_failure(
            error_message=rr.failure_reason if rr.status in ("ERROR", "TIMEOUT") else None,
            diff_json=rr.diff_result,
            diff_score=rr.diff_score,
            replayed_status_code=rr.actual_status_code,
            assertion_results=assertion_list,
        )

        if category not in categories:
            category = "UNKNOWN"

        categories[category]["count"] += 1
        categories[category]["results"].append({
            "id": rr.id,
            "test_case_id": rr.test_case_id,
            "request_method": rr.request_method,
            "request_uri": rr.request_uri,
            "status": rr.status,
            "actual_status_code": rr.actual_status_code,
            "diff_score": rr.diff_score,
            "failure_category": rr.failure_category,
            "failure_reason": rr.failure_reason,
            "analysis_reason": reason,
            "latency_ms": rr.latency_ms,
        })

    total_failures = len(fail_results)
    if total_failures > 0:
        for cat in categories:
            categories[cat]["percentage"] = round(
                categories[cat]["count"] / total_failures * 100, 1
            )

    return {
        "job_id": job_id,
        "total_failures": total_failures,
        "categories": categories,
    }


@router.websocket("/{job_id}/ws")
async def replay_progress_ws(job_id: int, websocket: WebSocket):
    """WebSocket endpoint for real-time replay progress."""
    token = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
    async with database.async_session_factory() as db:
        if not token or not await get_user_for_access_token(token, db):
            await websocket.close(code=1008)
            return

    await websocket.accept()
    await register_ws(job_id, websocket)
    try:
        async with database.async_session_factory() as db:
            result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
            job = result.scalar_one_or_none()
            if job:
                await websocket.send_json(
                    {
                        "job_id": job_id,
                        "done": job.passed + job.failed + job.errored,
                        "total": job.total,
                        "passed": job.passed,
                        "failed": job.failed,
                        "errored": job.errored,
                        "finished": job.status in ("DONE", "FAILED", "CANCELLED"),
                    }
                )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await unregister_ws(job_id, websocket)
