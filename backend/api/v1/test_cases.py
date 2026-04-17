"""Test case library management."""
import json
from typing import Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from database import get_db
from models.test_case import TestCase
from models.recording import Recording
from models.suite import Suite, SuiteCase
from schemas.test_case import (
    TestCaseCreate, TestCaseUpdate, TestCaseOut,
    TestCaseFromRecording, AddToSuiteRequest,
    BatchCheckRequest, BatchCheckItem,
    BatchFromRecordingsRequest, BatchResultItem, BatchFromRecordingsResponse,
)
from core.security import require_viewer, require_editor
from utils.governance import build_scene_key, infer_transaction_code, normalize_governance_status

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


def _fill_governance_fields(payload: dict) -> dict:
    transaction_code = payload.get("transaction_code") or infer_transaction_code(
        payload.get("request_body"),
        payload.get("expected_response"),
    )
    payload["transaction_code"] = transaction_code
    payload["governance_status"] = normalize_governance_status(payload.get("governance_status"), "candidate")
    payload["scene_key"] = payload.get("scene_key") or build_scene_key(
        transaction_code,
        payload.get("request_method"),
        payload.get("request_uri"),
        payload.get("expected_status"),
    )
    return payload


async def _validate_suite_entry(case_id: int, suite: Suite, db: AsyncSession) -> None:
    case_result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    test_case = case_result.scalar_one_or_none()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")

    if test_case.scene_key:
        existing_result = await db.execute(
            select(TestCase.id)
            .join(SuiteCase, SuiteCase.test_case_id == TestCase.id)
            .where(
                SuiteCase.suite_id == suite.id,
                TestCase.scene_key == test_case.scene_key,
                TestCase.id != case_id,
            )
        )
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=400,
                detail=f"Suite already contains a representative sample for scene_key: {test_case.scene_key}",
            )


@router.post("/batch-check", response_model=list[BatchCheckItem])
async def batch_check(
    body: BatchCheckRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    """Check which recordings already have a test case (by source_recording_id)."""
    if not body.recording_ids:
        return []

    # Fetch recordings
    rec_result = await db.execute(
        select(Recording).where(Recording.id.in_(body.recording_ids))
    )
    recordings = {r.id: r for r in rec_result.scalars().all()}

    # Fetch existing test cases that reference these recordings
    tc_result = await db.execute(
        select(TestCase).where(TestCase.source_recording_id.in_(body.recording_ids))
    )
    existing_by_rec: dict[int, TestCase] = {}
    for tc in tc_result.scalars().all():
        if tc.source_recording_id not in existing_by_rec:
            existing_by_rec[tc.source_recording_id] = tc

    items = []
    for rec_id in body.recording_ids:
        rec = recordings.get(rec_id)
        existing = existing_by_rec.get(rec_id)
        items.append(BatchCheckItem(
            recording_id=rec_id,
            transaction_code=rec.transaction_code if rec else None,
            has_existing=existing is not None,
            existing_case_id=existing.id if existing else None,
            existing_case_name=existing.name if existing else None,
        ))
    return items


@router.post("/batch-from-recordings", response_model=BatchFromRecordingsResponse)
async def batch_from_recordings(
    body: BatchFromRecordingsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Batch create test cases from a list of recording IDs with a shared name prefix."""
    results: list[BatchResultItem] = []
    created_count = 0
    failed_count = 0

    for rec_id in body.recording_ids:
        try:
            rec_result = await db.execute(select(Recording).where(Recording.id == rec_id))
            recording = rec_result.scalar_one_or_none()
            if not recording:
                results.append(BatchResultItem(
                    recording_id=rec_id,
                    status="failed",
                    error="Recording not found",
                ))
                failed_count += 1
                continue

            # Build name: prefix + transaction_code or fallback to method + uri
            suffix = recording.transaction_code or f"{recording.request_method} {recording.request_uri}"
            name = f"{body.prefix} - {suffix}"

            tc = TestCase(**_fill_governance_fields({
                "name": name,
                "application_id": recording.application_id,
                "source_recording_id": recording.id,
                "request_method": recording.request_method,
                "request_uri": recording.request_uri,
                "request_headers": recording.request_headers,
                "request_body": recording.request_body,
                "expected_status": recording.response_status,
                "expected_response": recording.response_body,
                "transaction_code": recording.transaction_code,
                "scene_key": recording.scene_key,
                "governance_status": recording.governance_status or "candidate",
                "status": "active",
            }))
            db.add(tc)
            await db.commit()
            await db.refresh(tc)

            results.append(BatchResultItem(
                recording_id=rec_id,
                status="created",
                test_case_id=tc.id,
                name=tc.name,
            ))
            created_count += 1

        except Exception as exc:
            await db.rollback()
            results.append(BatchResultItem(
                recording_id=rec_id,
                status="failed",
                error=str(exc),
            ))
            failed_count += 1

    return BatchFromRecordingsResponse(
        total=len(body.recording_ids),
        created=created_count,
        failed=failed_count,
        results=results,
    )


@router.get("/export")
async def export_test_cases(
    ids: Optional[str] = Query(None),
    application_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(TestCase)
    if ids:
        id_list = [int(i) for i in ids.split(",") if i.strip().isdigit()]
        stmt = stmt.where(TestCase.id.in_(id_list))
    elif application_id:
        stmt = stmt.where(TestCase.application_id == application_id)
    result = await db.execute(stmt)
    cases = result.scalars().all()
    return [TestCaseOut.model_validate(c).model_dump(mode="json") for c in cases]


@router.post("/from-recording", response_model=TestCaseOut, status_code=201)
async def create_from_recording(
    body: TestCaseFromRecording,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Recording).where(Recording.id == body.recording_id))
    recording = result.scalar_one_or_none()
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")

    name = body.name or f"{recording.request_method} {recording.request_uri}"

    # Extract expected response from response_body
    expected_response = recording.response_body

    tc = TestCase(**_fill_governance_fields({
        "name": name,
        "application_id": recording.application_id,
        "source_recording_id": recording.id,
        "request_method": recording.request_method,
        "request_uri": recording.request_uri,
        "request_headers": recording.request_headers,
        "request_body": recording.request_body,
        "expected_status": recording.response_status,
        "expected_response": expected_response,
        "tags": body.tags,
        "status": body.status,
        "transaction_code": recording.transaction_code,
        "scene_key": recording.scene_key,
        "governance_status": body.governance_status or recording.governance_status or "candidate",
    }))
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.post("/import", status_code=201)
async def import_test_cases(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    content = await file.read()
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    created = []
    for item in data:
        try:
            tc_data = TestCaseCreate(**item)
            tc = TestCase(**_fill_governance_fields(tc_data.model_dump()))
            db.add(tc)
            created.append(tc)
        except Exception:
            continue
    await db.commit()
    return {"imported": len(created)}


@router.get("", response_model=list[TestCaseOut])
async def list_test_cases(
    application_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    governance_status: Optional[str] = Query(None),
    transaction_code: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(TestCase)
    filters = []
    if application_id:
        filters.append(TestCase.application_id == application_id)
    if status:
        filters.append(TestCase.status == status)
    if governance_status:
        filters.append(TestCase.governance_status == governance_status)
    if transaction_code:
        filters.append(TestCase.transaction_code == transaction_code)
    if tags:
        filters.append(TestCase.tags.contains(tags))
    if search:
        filters.append(or_(
            TestCase.name.contains(search),
            TestCase.request_uri.contains(search),
            TestCase.transaction_code.contains(search),
        ))
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(TestCase.created_at.desc(), TestCase.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=TestCaseOut, status_code=201)
async def create_test_case(
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    tc = TestCase(**_fill_governance_fields(body.model_dump()))
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.get("/{case_id}", response_model=TestCaseOut)
async def get_test_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    return tc


@router.put("/{case_id}", response_model=TestCaseOut)
async def update_test_case(
    case_id: int,
    body: TestCaseUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(tc, field, value)
    if "transaction_code" in updates:
        tc.transaction_code = updates["transaction_code"] or infer_transaction_code(tc.request_body, tc.expected_response)
    else:
        tc.transaction_code = infer_transaction_code(tc.request_body, tc.expected_response) or tc.transaction_code
    tc.governance_status = normalize_governance_status(tc.governance_status, "candidate")
    tc.scene_key = build_scene_key(tc.transaction_code, tc.request_method, tc.request_uri, tc.expected_status)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.delete("/{case_id}", status_code=204)
async def delete_test_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    await db.delete(tc)
    await db.commit()


@router.post("/{case_id}/clone", response_model=TestCaseOut, status_code=201)
async def clone_test_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    tc = result.scalar_one_or_none()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    clone = TestCase(
        name=f"{tc.name} (copy)",
        description=tc.description,
        application_id=tc.application_id,
        source_recording_id=tc.source_recording_id,
        status="draft",
        governance_status=tc.governance_status,
        transaction_code=tc.transaction_code,
        scene_key=tc.scene_key,
        tags=tc.tags,
        request_method=tc.request_method,
        request_uri=tc.request_uri,
        request_headers=tc.request_headers,
        request_body=tc.request_body,
        expected_status=tc.expected_status,
        expected_response=tc.expected_response,
        assert_rules=tc.assert_rules,
        ignore_fields=tc.ignore_fields,
        perf_threshold_ms=tc.perf_threshold_ms,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone


@router.post("/{case_id}/add-to-suite", status_code=201)
async def add_to_suite(
    case_id: int,
    body: AddToSuiteRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    # Validate suite exists
    result = await db.execute(select(Suite).where(Suite.id == body.suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    await _validate_suite_entry(case_id, suite, db)
    # Check not already in suite
    existing = await db.execute(
        select(SuiteCase).where(
            and_(SuiteCase.suite_id == body.suite_id, SuiteCase.test_case_id == case_id)
        )
    )
    if existing.scalar_one_or_none():
        return {"message": "Already in suite"}
    # Get current max order
    from sqlalchemy import func
    max_order = await db.execute(
        select(func.max(SuiteCase.order_index)).where(SuiteCase.suite_id == body.suite_id)
    )
    next_order = (max_order.scalar() or 0) + 1
    sc = SuiteCase(suite_id=body.suite_id, test_case_id=case_id, order_index=next_order)
    db.add(sc)
    await db.commit()
    return {"message": "Added to suite", "order_index": next_order}
