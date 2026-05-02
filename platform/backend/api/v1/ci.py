"""CI/CD integration API: token management, trigger replay, poll result."""
import secrets
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.replay_context import infer_application_id_for_case_ids
from core.security import get_password_hash, require_admin, verify_password
from database import get_db
from models.ci import CiToken
from models.replay import ReplayJob, ReplayResult
from models.suite import Suite, SuiteCase
from schemas.ci import CiResultResponse, CiTokenCreate, CiTokenOut, CiTriggerRequest
from schemas.common import PageOut
from utils.timezone import now_beijing

router = APIRouter(prefix="/ci", tags=["ci"])


async def _get_ci_token(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> CiToken:
    """Validate CI token from Authorization header (format: 'Token <token>')."""
    if not authorization or not authorization.startswith("Token "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing CI token")
    plain_token = authorization.removeprefix("Token ").strip()

    result = await db.execute(select(CiToken).where(CiToken.is_active.is_(True)))
    tokens = result.scalars().all()
    for token in tokens:
        if verify_password(plain_token, token.token_hash):
            if token.expires_at and token.expires_at < now_beijing():
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="CI token expired")
            token.last_used_at = now_beijing()
            await db.commit()
            return token
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid CI token")


@router.get("/tokens", response_model=PageOut[CiTokenOut] | list[CiTokenOut])
async def list_tokens(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    include_total: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    stmt = select(CiToken).order_by(CiToken.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    if not include_total:
        return items

    total = await db.scalar(select(func.count()).select_from(CiToken))
    return PageOut[CiTokenOut](items=items, total=total or 0, skip=skip, limit=limit)


@router.post("/tokens", response_model=CiTokenOut, status_code=201)
async def create_token(
    body: CiTokenCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    plain_token = secrets.token_urlsafe(32)
    expires_at = None
    if body.expires_days:
        expires_at = now_beijing() + timedelta(days=body.expires_days)

    token = CiToken(
        name=body.name,
        token_hash=get_password_hash(plain_token),
        scope=body.scope,
        expires_at=expires_at,
    )
    db.add(token)
    await db.commit()
    await db.refresh(token)

    out = CiTokenOut.model_validate(token)
    out.plain_token = plain_token
    return out


@router.delete("/tokens/{token_id}", status_code=204)
async def revoke_token(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(CiToken).where(CiToken.id == token_id))
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found")
    token.is_active = False
    await db.commit()


@router.post("/trigger")
async def trigger_replay(
    body: CiTriggerRequest,
    db: AsyncSession = Depends(get_db),
    ci_token: CiToken = Depends(_get_ci_token),
):
    """Trigger a suite replay using CI token authentication."""
    if ci_token.scope != "trigger":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CI token scope 'trigger' is required to trigger replays",
        )

    import asyncio
    import core.replay_executor as replay_executor

    result = await db.execute(select(Suite).where(Suite.id == body.suite_id))
    suite = result.scalar_one_or_none()
    if not suite:
        raise HTTPException(status_code=404, detail="Suite not found")

    cases_result = await db.execute(
        select(SuiteCase.test_case_id)
        .where(SuiteCase.suite_id == body.suite_id)
        .order_by(SuiteCase.order_index)
    )
    case_ids = list(cases_result.scalars().all())
    if not case_ids:
        raise HTTPException(status_code=400, detail="Suite has no test cases")

    try:
        application_id = await infer_application_id_for_case_ids(db, case_ids)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if application_id is None:
        raise HTTPException(
            status_code=400,
            detail="Suite test cases must have an application_id before CI replay can be triggered",
        )

    job = ReplayJob(
        name=f"[CI] Suite {body.suite_id}",
        application_id=application_id,
        status="PENDING",
        concurrency=body.concurrency,
        timeout_ms=body.timeout_ms,
        total=len(case_ids),
        notify_type=body.notify_type,
        webhook_url=body.notify_webhook,
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    for case_id in case_ids:
        db.add(ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False))
    await db.commit()

    asyncio.create_task(replay_executor.run_replay_job(job.id))
    return {"job_id": job.id, "status": "PENDING", "total": len(case_ids)}


@router.get("/result/{job_id}", response_model=CiResultResponse)
async def get_result(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    ci_token: CiToken = Depends(_get_ci_token),
):
    """Poll replay job result using CI token."""
    result = await db.execute(select(ReplayJob).where(ReplayJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    pass_rate = (job.passed / job.total) if job.total > 0 else None
    return CiResultResponse(
        job_id=job.id,
        status=job.status,
        total=job.total,
        passed=job.passed,
        failed=job.failed,
        errored=job.errored,
        pass_rate=pass_rate,
    )
