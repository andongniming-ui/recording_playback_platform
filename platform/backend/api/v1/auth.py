from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import jwt
from jwt.exceptions import InvalidTokenError as JWTError

from database import get_db
from models.auth import RefreshToken
from models.user import User
from schemas.auth import LoginResponse, RefreshRequest, UserInfo
from core.security import (
    verify_password, create_access_token, create_refresh_token,
    get_current_user, get_password_hash, hash_token, ALGORITHM
)
from core.rate_limit import limiter
from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_TOKEN_COOKIE = "ar_refresh_token"


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE, path="/api/v1/auth")


async def _persist_refresh_token(
    db: AsyncSession,
    user: User,
    token: str,
    jti: str,
    expires_at,
) -> None:
    db.add(
        RefreshToken(
            jti=jti,
            user_id=user.id,
            username=user.username,
            token_hash=hash_token(token),
            expires_at=expires_at,
        )
    )


async def _revoke_refresh_token(
    db: AsyncSession,
    token: str,
    replaced_by_jti: str | None = None,
) -> bool:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError:
        return False
    jti = payload.get("jti")
    if not jti:
        return False
    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    stored = result.scalar_one_or_none()
    if not stored or stored.token_hash != hash_token(token):
        return False
    stored.revoked = True
    stored.revoked_at = _utc_now_naive()
    stored.replaced_by_jti = replaced_by_jti
    return True


@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    access_token = create_access_token({"sub": user.username})
    refresh_token, refresh_jti, refresh_expires_at = create_refresh_token({"sub": user.username})
    await _persist_refresh_token(db, user, refresh_token, refresh_jti, refresh_expires_at)
    await db.commit()
    _set_refresh_cookie(response, refresh_token)
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        username=user.username,
    )


@router.post("/refresh", response_model=LoginResponse)
async def refresh_token(
    response: Response,
    body: RefreshRequest | None = Body(default=None),
    cookie_refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    token = body.refresh_token if body and body.refresh_token else cookie_refresh_token
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if not username or not jti:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    token_result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    stored_token = token_result.scalar_one_or_none()
    if (
        not stored_token
        or stored_token.revoked
        or stored_token.token_hash != hash_token(token)
        or stored_token.expires_at < _utc_now_naive()
    ):
        raise credentials_exception

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise credentials_exception

    new_refresh_token, new_refresh_jti, new_refresh_expires_at = create_refresh_token({"sub": user.username})
    await _revoke_refresh_token(db, token, replaced_by_jti=new_refresh_jti)
    await _persist_refresh_token(db, user, new_refresh_token, new_refresh_jti, new_refresh_expires_at)
    await db.commit()
    _set_refresh_cookie(response, new_refresh_token)
    return LoginResponse(
        access_token=create_access_token({"sub": user.username}),
        refresh_token=new_refresh_token,
        role=user.role,
        username=user.username,
    )


@router.post("/logout")
async def logout(
    response: Response,
    body: RefreshRequest | None = Body(default=None),
    cookie_refresh_token: str | None = Cookie(default=None, alias=REFRESH_TOKEN_COOKIE),
    db: AsyncSession = Depends(get_db),
):
    token = body.refresh_token if body and body.refresh_token else cookie_refresh_token
    if token:
        await _revoke_refresh_token(db, token)
        await db.commit()
    _clear_refresh_cookie(response)
    return {"ok": True}


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
