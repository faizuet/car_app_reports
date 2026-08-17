from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.async_db import get_async_db, get_neo4j_service, Neo4jService
from app.models.user_model import User
from app.schemas.user_schema import (
    UserCreateSchema,
    UserLoginSchema,
    UserOutSchema,
    TokenSchema,
)
from app.deps.auth import security

# --- Dependency Aliases ---
DBSession = Annotated[AsyncSession, Depends(get_async_db)]
Neo4jDep = Annotated[Neo4jService, Depends(get_neo4j_service)]

router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by email (case-insensitive)."""
    result = await db.execute(select(User).where(User.email == email.strip().lower()))
    return result.scalars().first()


@router.post(
    "/signup",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_in: UserCreateSchema,
    db: DBSession,
    neo4j: Neo4jDep,
) -> User:
    """Register a new user and mirror it in Neo4j."""

    # Check email uniqueness
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Check username uniqueness
    existing_username = await db.execute(
        select(User).where(User.username == user_in.username.strip())
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    # Create user in PostgreSQL
    user = User.create(
        username=user_in.username.strip(),
        email=user_in.email.strip().lower(),
        password=user_in.password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Mirror user in Neo4j
    async def create_user_node(tx, user_id: int, username: str, email: str):
        await tx.run(
            """
            MERGE (u:User {id: $user_id})
            SET u.username = $username,
                u.email = $email
            """,
            user_id=user_id,
            username=username,
            email=email,
        )

    await neo4j.write(create_user_node, user_id=user.id, username=user.username, email=user.email)

    return user


@router.post("/login", response_model=TokenSchema)
async def login(
    data: UserLoginSchema,
    db: DBSession,
) -> TokenSchema:
    """Authenticate a user and return a JWT token."""

    user = await get_user_by_email(db, data.email)
    if not user or not user.check_password(data.password.strip()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = security.create_access_token(subject=str(user.id))
    return TokenSchema(access_token=token, token_type="bearer")

