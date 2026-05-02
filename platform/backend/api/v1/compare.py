"""Compare rules management API."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from database import get_db
from models.compare import CompareRule
from core.security import require_viewer, require_editor
from schemas.common import PageOut

router = APIRouter(prefix="/compare-rules", tags=["compare"])


class CompareRuleCreate(BaseModel):
    name: str
    scope: str = "global"       # 'global'/'app'
    application_id: Optional[int] = None
    rule_type: str              # 'ignore'/'assert'
    config: str                 # JSON配置
    is_active: bool = True


class CompareRuleUpdate(BaseModel):
    name: Optional[str] = None
    scope: Optional[str] = None
    rule_type: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None


class CompareRuleOut(BaseModel):
    id: int
    name: str
    scope: str
    application_id: Optional[int]
    rule_type: str
    config: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=PageOut[CompareRuleOut] | list[CompareRuleOut])
async def list_rules(
    scope: Optional[str] = Query(None),
    application_id: Optional[int] = Query(None),
    rule_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    conditions = []
    if scope:
        conditions.append(CompareRule.scope == scope)
    if application_id:
        conditions.append(CompareRule.application_id == application_id)
    if rule_type:
        conditions.append(CompareRule.rule_type == rule_type)

    stmt = select(CompareRule)
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.order_by(CompareRule.id.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if not include_total:
        return items

    count_stmt = select(func.count()).select_from(CompareRule)
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = await db.scalar(count_stmt)
    return PageOut[CompareRuleOut](items=items, total=total or 0, skip=skip, limit=limit)


@router.post("", response_model=CompareRuleOut, status_code=201)
async def create_rule(
    body: CompareRuleCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    rule = CompareRule(**body.model_dump())
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=CompareRuleOut)
async def get_rule(rule_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_viewer)):
    result = await db.execute(select(CompareRule).where(CompareRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=CompareRuleOut)
async def update_rule(
    rule_id: int,
    body: CompareRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_editor),
):
    result = await db.execute(select(CompareRule).where(CompareRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(rule_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_editor)):
    result = await db.execute(select(CompareRule).where(CompareRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    await db.delete(rule)
    await db.commit()
