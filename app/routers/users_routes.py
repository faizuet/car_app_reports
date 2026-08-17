from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user_model import User
from app.schemas.user_schema import UserOutSchema, UserUpdateSchema, UserCreateSchema
from app.core.async_db import get_async_db, get_neo4j_service, Neo4jService
from app.deps.auth import get_current_user
from app.utils.cursor_pagination import cursor_paginate, CursorPage
from app.utils.neo4j_service import create_user_node_async


# --- Dependency Aliases ---
DBSession = Annotated[AsyncSession, Depends(get_async_db)]
Neo4jDep = Annotated[Neo4jService, Depends(get_neo4j_service)]
CurrentUser = Annotated[dict, Depends(get_current_user)]

router = APIRouter(prefix="/users", tags=["Users"])


async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    """Fetch a user or raise 404."""
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- Routes ---

@router.get("/", response_model=CursorPage[UserOutSchema])
async def list_users(
    db: DBSession,
    limit: int = 10,
    cursor: Optional[int] = None,
):
    """Paginated list of all users."""
    query = select(User).order_by(User.id)
    return await cursor_paginate(query, db, schema=UserOutSchema, limit=limit, cursor=cursor)


@router.post("/", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateSchema, db: DBSession, neo4j: Neo4jDep):
    """Register a new user and sync with Neo4j."""
    # 1. Check if email already exists
    existing_user = (
        (await db.execute(select(User).where(User.email == data.email.lower())))
        .scalars()
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")

    # 2. Create in PostgreSQL
    user = User(username=data.username.strip(), email=data.email.strip().lower())
    user.set_password(data.password.strip())
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 3. Mirror to Neo4j
    async def create_user_node(tx):
        await create_user_node_async(
            tx,
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=str(user.created_at),
            updated_at=str(user.updated_at),
        )

    await neo4j.write(create_user_node)

    return user


@router.get("/me", response_model=UserOutSchema)
async def get_profile(
    db: DBSession,
    current_user: CurrentUser,
):
    """Return the logged-in user's profile."""
    return await get_user_or_404(db, int(current_user["sub"]))


@router.put("/me", response_model=UserOutSchema)
async def update_profile(
    data: UserUpdateSchema,
    db: DBSession,
    neo4j: Neo4jDep,
    current_user: CurrentUser,
):
    """Update the authenticated user's profile and sync with Neo4j."""
    user = await get_user_or_404(db, int(current_user["sub"]))

    # Update username
    if data.username:
        user.username = data.username.strip()

    # Update email with uniqueness check
    if data.email:
        email = data.email.strip().lower()
        existing_user = (await db.execute(select(User).where(User.email == email))).scalars().first()
        if existing_user and existing_user.id != user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        user.email = email

    # Update password
    if data.password:
        user.set_password(data.password.strip())

    await db.commit()
    await db.refresh(user)

    # Mirror update to Neo4j
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

    return user

