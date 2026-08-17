from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_model import User
from app.schemas.user_schema import (
    UserOutSchema,
    UserUpdateSchema,
    UserCreateSchema,
    PasswordChangeSchema,
)
from app.core.async_db import get_async_db, get_neo4j_service, Neo4jService
from app.deps.auth import get_current_user
from app.utils.cursor_pagination import cursor_paginate, CursorPage
from app.utils.neo4j_service import create_user_node_async
from app.utils.upload import save_avatar, delete_avatar_file

DBSession = Annotated[AsyncSession, Depends(get_async_db)]
Neo4jDep = Annotated[Neo4jService, Depends(get_neo4j_service)]
CurrentUser = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def _sync_user_to_neo4j(neo4j: Neo4jService, user: User) -> None:
    async def update_user_node(tx):
        await create_user_node_async(
            tx,
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at),
        )

    await neo4j.write(update_user_node)


@router.get("/", response_model=CursorPage[UserOutSchema])
async def list_users(
    db: DBSession,
    limit: int = 10,
    cursor: Optional[int] = None,
):
    query = select(User).order_by(User.id)
    return await cursor_paginate(query, db, schema=UserOutSchema, limit=limit, cursor=cursor)


@router.post("/", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateSchema, db: DBSession, neo4j: Neo4jDep):
    existing_user = (
        (await db.execute(select(User).where(User.email == data.email.lower())))
        .scalars()
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    user = User(username=data.username.strip(), email=data.email.strip().lower())
    user.set_password(data.password.strip())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await _sync_user_to_neo4j(neo4j, user)
    return user


@router.get("/me", response_model=UserOutSchema)
async def get_profile(db: DBSession, current_user: CurrentUser):
    return await get_user_or_404(db, int(current_user["sub"]))


@router.put("/me", response_model=UserOutSchema)
async def update_profile(
    data: UserUpdateSchema,
    db: DBSession,
    neo4j: Neo4jDep,
    current_user: CurrentUser,
):
    user = await get_user_or_404(db, int(current_user["sub"]))

    if data.username:
        existing = (
            await db.execute(select(User).where(User.username == data.username.strip()))
        ).scalars().first()
        if existing and existing.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        user.username = data.username.strip()

    if data.display_name is not None:
        user.display_name = data.display_name.strip() if data.display_name else None

    if data.email:
        email = data.email.strip().lower()
        existing_user = (await db.execute(select(User).where(User.email == email))).scalars().first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = email

    if data.bio is not None:
        user.bio = data.bio.strip() if data.bio else None

    if data.phone is not None:
        user.phone = data.phone.strip() if data.phone else None

    await db.commit()
    await db.refresh(user)
    await _sync_user_to_neo4j(neo4j, user)
    return user


@router.put("/me/password", response_model=UserOutSchema)
async def change_password(
    data: PasswordChangeSchema,
    db: DBSession,
    current_user: CurrentUser,
):
    user = await get_user_or_404(db, int(current_user["sub"]))

    if not user.check_password(data.current_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.set_password(data.new_password)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/me/avatar", response_model=UserOutSchema)
async def upload_avatar(
    db: DBSession,
    current_user: CurrentUser,
    file: UploadFile = File(...),
):
    user = await get_user_or_404(db, int(current_user["sub"]))

    if user.profile_image:
        delete_avatar_file(user.profile_image)

    user.profile_image = save_avatar(user.id, file)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/me/avatar", response_model=UserOutSchema)
async def remove_avatar(db: DBSession, current_user: CurrentUser):
    user = await get_user_or_404(db, int(current_user["sub"]))

    if user.profile_image:
        delete_avatar_file(user.profile_image)
        user.profile_image = None
        await db.commit()
        await db.refresh(user)

    return user
