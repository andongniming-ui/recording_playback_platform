"""Schedule management API."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.schedule import Schedule
from schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from core.security import require_viewer, require_editor
from core.scheduler import add_schedule, remove_schedule, trigger_now

router = APIRouter(prefix="/schedules", tags=["schedules"])


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
    await trigger_now(schedule_id)
    return {"message": f"Schedule {schedule_id} triggered"}
