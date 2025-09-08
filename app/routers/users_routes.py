from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_model import User
from app.schemas.user_schema import UserOutSchema, UserUpdateSchema
from app.core.async_db import get_async_db
from app.deps.auth import get_current_user
from app.utils.cursor_pagination import cursor_paginate, CursorPage


router = APIRouter(prefix="/users", tags=["Users"])

async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    """Fetch a user by ID or raise 404 if not found."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/", response_model=CursorPage[UserOutSchema])
async def list_users(
    db: AsyncSession = Depends(get_async_db),
    limit: int = 10,
    cursor: int | None = None,
):
    """Get paginated list of all users (admin use-case)."""
    query = select(User).order_by(User.id)
    return await cursor_paginate(query, db, schema=UserOutSchema, limit=limit, cursor=cursor)


@router.get("/me", response_model=UserOutSchema)
async def get_profile(
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    """Get the currently authenticated user's profile."""
    return await get_user_or_404(db, int(current_user["sub"]))


@router.put("/me", response_model=UserOutSchema)
async def update_profile(
    data: UserUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: dict = Depends(get_current_user),
):
    """Update the authenticated user's profile."""
    user = await get_user_or_404(db, int(current_user["sub"]))

    # Update username
    if data.username:
        user.username = data.username.strip()

    # Update email with uniqueness check
    if data.email:
        email = data.email.strip().lower()
        existing_user = (
            await db.execute(select(User).where(User.email == email))
        ).scalars().first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = email

    # Update password
    if data.password:
        user.set_password(data.password.strip())

    await db.commit()
    await db.refresh(user)
    return user

