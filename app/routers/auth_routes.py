from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.async_db import get_async_db
from app.models.user_model import User
from app.schemas.user_schema import (
    UserRegisterSchema,
    UserOutSchema,
    UserLoginSchema,
    TokenSchema,
)
from app.deps.auth import security


router = APIRouter(prefix="/auth", tags=["Auth"])


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by email (case-insensitive)."""
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalars().first()

@router.post(
    "/signup",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_in: UserRegisterSchema,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """Register a new user with unique email and username."""

    # Check if email already exists
    if await get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = await db.execute(
        select(User).where(User.username == user_in.username.strip())
    )
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create and persist user
    user = User.create(
        username=user_in.username.strip(),
        email=user_in.email.strip().lower(),
        password=user_in.password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenSchema)
async def login(
    data: UserLoginSchema,
    db: AsyncSession = Depends(get_async_db),
) -> TokenSchema:
    """Authenticate a user and return a JWT token."""

    user = await get_user_by_email(db, data.email)
    if not user or not user.check_password(data.password.strip()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT
    token = security.create_access_token(subject=str(user.id))

    return TokenSchema(access_token=token, token_type="bearer")

