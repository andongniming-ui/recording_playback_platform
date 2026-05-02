"""Test suite management API."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.replay_context import infer_application_id_for_case_ids
from core.security import require_editor, require_viewer
from database import get_db
from models.test_case import TestCase
from models.suite import Suite, SuiteCase
from schemas.suite import (
    AutoSmokeSuiteCreate,
    AutoSmokeSuiteResult,
    ReorderRequest,
    SetCasesRequest,
    SuiteCreate,
    SuiteOut,
    SuiteRunRequest,
    SuiteUpdate,
    SuiteWithCases,
)
from schemas.common import BulkDeleteResponse, BulkIdsRequest, PageOut
from utils.governance import normalize_suite_type
from utils.query import apply_ordering

router = APIRouter(prefix="/suites", tags=["suites"])


async def _validate_suite_case_selection(suite: Suite, case_ids: list[int], db: AsyncSession) -> None:
    if not case_ids:
        return
    result = await db.execute(select(TestCase).where(TestCase.id.in_(case_ids)))
    cases = result.scalars().all()
    found_ids = {case.id for case in cases}
    missing_ids = [case_id for case_id in case_ids if case_id not in found_ids]
    if missing_ids:
        raise HTTPException(status_code=404, detail=f"Test case not found: {missing_ids[0]}")


    scene_key_map: dict[str, str] = {}
    for case in cases:
        if not case.scene_key:
            continue
        if case.scene_key in scene_key_map:
            raise HTTPException(
                status_code=400,
                detail=f"Duplicate scene_key in suite selection: {case.scene_key}",
            )
        scene_key_map[case.scene_key] = case.name


def _suite_case_sort_key(test_case: TestCase) -> tuple[int, object, int]:
    status_priority = 1 if test_case.status == "active" else 0
    updated_at = test_case.updated_at or test_case.created_at
    return (status_priority, updated_at, test_case.id)


@router.get("", response_model=PageOut[SuiteOut] | list[SuiteOut])
async def list_suites(
    suite_type: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(Suite)
    if suite_type:
        stmt = stmt.where(Suite.suite_type == normalize_suite_type(suite_type))
    total = None
    if include_total:
        total_result = await db.execute(select(func.count()).select_from(stmt.subquery()))
        total = total_result.scalar_one()
    sort_mapping = {
        "created_at": Suite.created_at,
        "updated_at": Suite.updated_at,
        "name": Suite.name,
        "id": Suite.id,
    }
    primary_column = sort_mapping.get(sort_by, Suite.created_at)
    stmt = apply_ordering(stmt, primary_column, Suite.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if include_total:
        return PageOut[SuiteOut](items=items, total=total or 0, skip=skip, limit=limit)
    return items


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_suites(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    suite_ids = sorted({suite_id for suite_id in body.ids if suite_id})
    if not suite_ids:
        return BulkDeleteResponse(deleted=0)

    result = await db.execute(select(Suite).where(Suite.id.in_(suite_ids)))
    suites = result.scalars().all()
    if not suites:
        return BulkDeleteResponse(deleted=0)

    delete_ids = [suite.id for suite in suites]
    await db.execute(delete(SuiteCase).where(SuiteCase.suite_id.in_(delete_ids)))
    await db.execute(delete(Suite).where(Suite.id.in_(delete_ids)))
    await db.commit()
    return BulkDeleteResponse(deleted=len(delete_ids))


@router.post("", response_model=SuiteOut, status_code=201)
async def create_suite(
    body: SuiteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    payload = body.model_dump()
    payload["suite_type"] = normalize_suite_type(payload.get("suite_type"))
    suite = Suite(**payload)
    db.add(suite)
    await db.commit()
    await db.refresh(suite)
    return suite


@router.post("/auto-smoke", response_model=AutoSmokeSuiteResult, status_code=201)
async def create_auto_smoke_suite(
    body: AutoSmokeSuiteCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    stmt = (
        select(TestCase)
        .where(
            TestCase.application_id == body.application_id,
            TestCase.transaction_code.is_not(None),
        )
        .order_by(TestCase.transaction_code.asc(), TestCase.updated_at.desc(), TestCase.created_at.desc())
    )
    result = await db.execute(stmt)
    cases = result.scalars().all()
    if not cases:
        raise HTTPException(status_code=400, detail="No test cases with transaction_code found for this application")

    by_transaction: dict[str, list[TestCase]] = {}
    for test_case in cases:
        if not test_case.transaction_code:
            continue
        by_transaction.setdefault(test_case.transaction_code, []).append(test_case)

    selected_cases: list[TestCase] = []
    skipped_transaction_codes: list[str] = []
    for transaction_code, items in by_transaction.items():
        scene_key_seen: set[str] = set()
        representative = max(items, key=_suite_case_sort_key)
        if representative.scene_key:
            scene_key_seen.add(representative.scene_key)
        selected_cases.append(representative)
        duplicate_scenes = {
            item.scene_key
            for item in items
            if item.scene_key and item.scene_key in scene_key_seen and item.id != representative.id
        }
        if duplicate_scenes and transaction_code not in skipped_transaction_codes:
            skipped_transaction_codes.append(transaction_code)

    suite = Suite(
        name=body.name or f"Smoke Suite App #{body.application_id}",
        description=body.description or "按交易码自动生成的冒烟套件",
        suite_type="smoke",
    )
    db.add(suite)
    await db.commit()
    await db.refresh(suite)

    await _validate_suite_case_selection(suite, [item.id for item in selected_cases], db)
    for idx, test_case in enumerate(selected_cases):
        db.add(SuiteCase(suite_id=suite.id, test_case_id=test_case.id, order_index=idx))
    await db.commit()

    return AutoSmokeSuiteResult(
        suite_id=suite.id,
        name=suite.name,
        added_case_ids=[item.id for item in selected_cases],
        skipped_transaction_codes=sorted(skipped_transaction_codes),
    )


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
        suite_type=suite.suite_type,
        created_at=suite.created_at,
        updated_at=suite.updated_at,
        cases=[{"test_case_id": case.test_case_id, "order_index": case.order_index} for case in cases],
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
    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "suite_type":
            value = normalize_suite_type(value)
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
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")
    await _validate_suite_case_selection(suite, body.case_ids, db)

    await db.execute(delete(SuiteCase).where(SuiteCase.suite_id == suite_id))

    for idx, case_id in enumerate(body.case_ids):
        db.add(SuiteCase(suite_id=suite_id, test_case_id=case_id, order_index=idx))
    await db.commit()

    return await get_suite(suite_id, db)


@router.post("/{suite_id}/reorder")
async def reorder_suite_cases(
    suite_id: int,
    body: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    for item in body.items:
        result = await db.execute(
            select(SuiteCase).where(
                SuiteCase.suite_id == suite_id,
                SuiteCase.test_case_id == item.test_case_id,
            )
        )
        suite_case = result.scalar_one_or_none()
        if suite_case:
            suite_case.order_index = item.order_index
    await db.commit()
    return {"message": "Reordered"}


@router.post("/{suite_id}/run", status_code=201)
async def run_suite(
    suite_id: int,
    body: SuiteRunRequest = SuiteRunRequest(),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Run all test cases in a suite as a replay job with configurable options."""
    import asyncio
    import json
    import core.replay_executor as replay_executor
    from models.replay import ReplayJob, ReplayResult

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

    # 确定回放目标应用：优先用户指定，其次从用例推断
    if body.target_application_id is not None:
        application_id = body.target_application_id
    else:
        try:
            application_id = await infer_application_id_for_case_ids(db, case_ids)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

        if application_id is None:
            raise HTTPException(
                status_code=400,
                detail="Suite test cases must have an application_id before replay can be started",
            )

    job = ReplayJob(
        name=f"Suite Run: {suite.name}",
        application_id=application_id,
        status="PENDING",
        concurrency=max(1, min(50, body.concurrency)),
        timeout_ms=max(1, body.timeout_ms),
        total=len(case_ids),
        ignore_fields=json.dumps(body.ignore_fields, ensure_ascii=False) if body.ignore_fields else None,
        smart_noise_reduction=body.smart_noise_reduction,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in case_ids:
        db.add(ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False))
    await db.commit()

    asyncio.create_task(replay_executor.run_replay_job(job.id))
    return {"message": "Suite replay started", "job_id": job.id}
