"""CI/CD integration API: token management, trigger replay, poll result."""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.ci import CiToken
from models.replay import ReplayJob, ReplayResult
from models.suite import Suite, SuiteCase
from schemas.ci import CiTokenCreate, CiTokenOut, CiTriggerRequest, CiResultResponse
from core.security import require_admin, require_viewer, get_password_hash, verify_password

router = APIRouter(prefix="/ci", tags=["ci"])


async def _get_ci_token(authorization: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> CiToken:
    """Validate CI token from Authorization header (format: 'Token <token>')."""
    if not authorization or not authorization.startswith("Token "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing CI token")
    plain_token = authorization.removeprefix("Token ").strip()

    # Check all active tokens (token_hash is bcrypt of plain token)
    result = await db.execute(select(CiToken).where(CiToken.is_active == True))
    tokens = result.scalars().all()
    for tok in tokens:
        if verify_password(plain_token, tok.token_hash):
            # Check expiry
            if tok.expires_at and tok.expires_at < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="CI token expired")
            # Update last_used_at
            tok.last_used_at = datetime.now(timezone.utc)
            await db.commit()
            return tok
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid CI token")


# ── Token management (admin only) ────────────────────────────────────────────

@router.get("/tokens", response_model=list[CiTokenOut])
async def list_tokens(db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    result = await db.execute(select(CiToken).order_by(CiToken.created_at.desc()))
    return result.scalars().all()


@router.post("/tokens", response_model=CiTokenOut, status_code=201)
async def create_token(
    body: CiTokenCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    plain_token = secrets.token_urlsafe(32)
    expires_at = None
    if body.expires_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_days)

    tok = CiToken(
        name=body.name,
        token_hash=get_password_hash(plain_token),
        scope=body.scope,
        expires_at=expires_at,
    )
    db.add(tok)
    await db.commit()
    await db.refresh(tok)

    out = CiTokenOut.model_validate(tok)
    out.plain_token = plain_token   # only returned once
    return out


@router.delete("/tokens/{token_id}", status_code=204)
async def revoke_token(
    token_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_admin),
):
    result = await db.execute(select(CiToken).where(CiToken.id == token_id))
    tok = result.scalar_one_or_none()
    if not tok:
        raise HTTPException(status_code=404, detail="Token not found")
    tok.is_active = False
    await db.commit()


# ── Trigger & poll (CI token auth) ───────────────────────────────────────────

@router.post("/trigger")
async def trigger_replay(
    body: CiTriggerRequest,
    db: AsyncSession = Depends(get_db),
    ci_token: CiToken = Depends(_get_ci_token),
):
    """Trigger a suite replay using CI token authentication."""
    # Enforce scope: only 'trigger' tokens can trigger replays
    if ci_token.scope != "trigger":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CI token scope 'trigger' is required to trigger replays",
        )
    import asyncio
    from models.replay import ReplayJob, ReplayResult
    from core.replay_executor import run_replay_job

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

    job = ReplayJob(
        name=f"[CI] Suite {body.suite_id}",
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
        r = ReplayResult(job_id=job.id, test_case_id=case_id, status="PENDING", is_pass=False)
        db.add(r)
    await db.commit()

    asyncio.create_task(run_replay_job(job.id))
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
