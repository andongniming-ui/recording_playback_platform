"""Test suite management API."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from database import get_db
from models.suite import Suite, SuiteCase
from models.test_case import TestCase
from schemas.suite import SuiteCreate, SuiteUpdate, SuiteOut, SuiteWithCases, SetCasesRequest, ReorderRequest
from core.security import require_viewer, require_editor

router = APIRouter(prefix="/suites", tags=["suites"])


@router.get("", response_model=list[SuiteOut])
async def list_suites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(Suite).order_by(Suite.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=SuiteOut, status_code=201)
async def create_suite(
    body: SuiteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    suite = Suite(**body.model_dump())
    db.add(suite)
    await db.commit()
    await db.refresh(suite)
    return suite


@router.get("/{suite_id}", response_model=SuiteWithCases)
async def get_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    cases_result = await db.execute(
        select(SuiteCase)
        .where(SuiteCase.suite_id == suite_id)
        .order_by(SuiteCase.order_index)
    )
    cases = cases_result.scalars().all()

    return SuiteWithCases(
        id=suite.id,
        name=suite.name,
        description=suite.description,
        created_at=suite.created_at,
        updated_at=suite.updated_at,
        cases=[{"test_case_id": c.test_case_id, "order_index": c.order_index} for c in cases],
    )


@router.put("/{suite_id}", response_model=SuiteOut)
async def update_suite(
    suite_id: int,
    body: SuiteUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(suite, field, value)
    await db.commit()
    await db.refresh(suite)
    return suite


@router.delete("/{suite_id}", status_code=204)
async def delete_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    await db.execute(delete(SuiteCase).where(SuiteCase.suite_id == suite_id))
    await db.delete(suite)
    await db.commit()


@router.put("/{suite_id}/cases", response_model=SuiteWithCases)
async def set_suite_cases(
    suite_id: int,
    body: SetCasesRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Replace all cases in the suite with the provided ordered list."""
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    # Delete existing
    await db.execute(delete(SuiteCase).where(SuiteCase.suite_id == suite_id))

    # Re-add in order
    for idx, case_id in enumerate(body.case_ids):
        sc = SuiteCase(suite_id=suite_id, test_case_id=case_id, order_index=idx)
        db.add(sc)
    await db.commit()

    return await get_suite(suite_id, db)


@router.post("/{suite_id}/reorder")
async def reorder_suite_cases(
    suite_id: int,
    body: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Update order_index for existing suite cases."""
    for item in body.items:
        result = await db.execute(
            select(SuiteCase).where(
                SuiteCase.suite_id == suite_id,
                SuiteCase.test_case_id == item.test_case_id,
            )
        )
        sc = result.scalar_one_or_none()
        if sc:
            sc.order_index = item.order_index
    await db.commit()
    return {"message": "Reordered"}


@router.post("/{suite_id}/run", status_code=201)
async def run_suite(
    suite_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Immediately run all test cases in the suite as a replay job."""
    import asyncio
    from models.replay import ReplayJob, ReplayResult
    from core.replay_executor import run_replay_job

    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    cases_result = await db.execute(
        select(SuiteCase.test_case_id)
        .where(SuiteCase.suite_id == suite_id)
        .order_by(SuiteCase.order_index)
    )
    case_ids = list(cases_result.scalars().all())
    if not case_ids:
        raise HTTPException(status_code=400, detail="Suite has no test cases")

    job = ReplayJob(
        name=f"Suite Run: {suite.name}",
        status="PENDING",
        concurrency=5,
        timeout_ms=5000,
        total=len(case_ids),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in case_ids:
        r = ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False)
        db.add(r)
    await db.commit()

    asyncio.create_task(run_replay_job(job.id))
    return {"message": "Suite replay started", "job_id": job.id}
