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
    TestCaseFromRecording, AddToSuiteRequest
)
from core.security import require_viewer, require_editor

router = APIRouter(prefix="/test-cases", tags=["test-cases"])


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

    tc = TestCase(
        name=name,
        application_id=recording.application_id,
        source_recording_id=recording.id,
        request_method=recording.request_method,
        request_uri=recording.request_uri,
        request_headers=recording.request_headers,
        request_body=recording.request_body,
        expected_status=recording.response_status,
        expected_response=expected_response,
        tags=body.tags,
        status=body.status,
    )
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
            tc = TestCase(**tc_data.model_dump())
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
    tags: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(TestCase)
    filters = []
    if application_id:
        filters.append(TestCase.application_id == application_id)
    if status:
        filters.append(TestCase.status == status)
    if tags:
        filters.append(TestCase.tags.contains(tags))
    if search:
        filters.append(or_(
            TestCase.name.contains(search),
            TestCase.request_uri.contains(search),
        ))
    if filters:
        stmt = stmt.where(and_(*filters))
    stmt = stmt.order_by(TestCase.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=TestCaseOut, status_code=201)
async def create_test_case(
    body: TestCaseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    tc = TestCase(**body.model_dump())
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
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(tc, field, value)
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
    # Validate case exists
    result = await db.execute(select(TestCase).where(TestCase.id == case_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Test case not found")
    # Validate suite exists
    result = await db.execute(select(Suite).where(Suite.id == body.suite_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Suite not found")
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
