"""Schedule management API."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.replay_context import infer_application_id_for_case_ids
from database import get_db
from models.schedule import Schedule
from models.suite import Suite, SuiteCase
from schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from core.security import require_viewer, require_editor
from core.scheduler import add_schedule, remove_schedule, trigger_now

router = APIRouter(prefix="/schedules", tags=["schedules"])


async def _validate_suite_exists(suite_id: Optional[int], db: AsyncSession):
    if suite_id is None:
        return
    result = await db.execute(select(Suite).where(Suite.id == suite_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Suite not found")


async def _validate_schedule_can_run(schedule: Schedule, db: AsyncSession):
    if schedule.suite_id is None:
        raise HTTPException(status_code=400, detail="Schedule must be bound to a suite before it can run")

    suite_result = await db.execute(select(Suite).where(Suite.id == schedule.suite_id))
    if not suite_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Suite not found")

    cases_result = await db.execute(
        select(SuiteCase.test_case_id)
        .where(SuiteCase.suite_id == schedule.suite_id)
        .order_by(SuiteCase.order_index)
    )
    case_ids = list(cases_result.scalars().all())
    if not case_ids:
        raise HTTPException(status_code=400, detail="Schedule suite has no test cases")

    try:
        application_id = await infer_application_id_for_case_ids(db, case_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if application_id is None:
        raise HTTPException(
            status_code=400,
            detail="Schedule suite test cases must have an application_id before execution can start",
        )


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(Schedule).order_by(Schedule.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(
    body: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    await _validate_suite_exists(body.suite_id, db)
    sched = Schedule(**body.model_dump())
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    if sched.is_active:
        add_schedule(sched.id, sched.cron_expr)
    return sched


@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return sched


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    body: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    await _validate_suite_exists(body.suite_id, db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(sched, field, value)

    await db.commit()
    await db.refresh(sched)

    # Re-register with scheduler
    remove_schedule(schedule_id)
    if sched.is_active:
        add_schedule(sched.id, sched.cron_expr)

    return sched


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    remove_schedule(schedule_id)
    await db.delete(sched)
    await db.commit()


@router.post("/{schedule_id}/trigger")
async def trigger_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    """Immediately trigger a scheduled replay."""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    sched = result.scalar_one_or_none()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await _validate_schedule_can_run(sched, db)
    await trigger_now(schedule_id)
    return {"message": f"Schedule {schedule_id} triggered"}
