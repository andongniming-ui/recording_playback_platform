"""Compare rules management API."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.compare import CompareRule
from core.security import require_viewer, require_editor

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


@router.get("", response_model=list[CompareRuleOut])
async def list_rules(
    scope: Optional[str] = Query(None),
    application_id: Optional[int] = Query(None),
    rule_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_viewer),
):
    stmt = select(CompareRule)
    if scope:
        stmt = stmt.where(CompareRule.scope == scope)
    if application_id:
        stmt = stmt.where(CompareRule.application_id == application_id)
    if rule_type:
        stmt = stmt.where(CompareRule.rule_type == rule_type)
    result = await db.execute(stmt)
    return result.scalars().all()


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
