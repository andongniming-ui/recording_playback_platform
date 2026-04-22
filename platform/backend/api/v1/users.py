from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, asc, desc

from database import get_db
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserOut
from schemas.common import BulkDeleteResponse, BulkIdsRequest
from core.security import get_password_hash, require_admin

router = APIRouter(prefix="/users", tags=["users"])


def _normalize_sort_order(value: str | None) -> str:
    return "asc" if (value or "").lower() == "asc" else "desc"


def _apply_ordering(stmt, primary_column, id_column, sort_order: str):
    direction = asc if _normalize_sort_order(sort_order) == "asc" else desc
    return stmt.order_by(direction(primary_column), direction(id_column))


@router.get("", response_model=list[UserOut])
async def list_users(
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    sort_mapping = {
        "created_at": User.created_at,
        "username": User.username,
        "role": User.role,
        "id": User.id,
    }
    primary_column = sort_mapping.get(sort_by, User.created_at)
    stmt = _apply_ordering(select(User), primary_column, User.id, sort_order).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/bulk-delete", response_model=BulkDeleteResponse)
async def bulk_delete_users(
    body: BulkIdsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    user_ids = sorted({user_id for user_id in body.ids if user_id})
    if not user_ids:
        return BulkDeleteResponse(deleted=0)
    if current_user.id in user_ids:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    result = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = result.scalars().all()
    if not users:
        return BulkDeleteResponse(deleted=0)

    await db.execute(delete(User).where(User.id.in_([item.id for item in users])))
    await db.commit()
    return BulkDeleteResponse(deleted=len(users))


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = await db.execute(select(User).where(User.username == body.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=body.username,
        hashed_password=get_password_hash(body.password),
        role=body.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password is not None:
        user.hashed_password = get_password_hash(body.password)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
