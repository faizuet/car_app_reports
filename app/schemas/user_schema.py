from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    """Schema for user registration / creation."""
    username: str = Field(..., min_length=3, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLoginSchema(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdateSchema(BaseModel):
    """Schema for updating user details."""
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class UserReadSchema(BaseModel):
    """Schema for reading user data."""
    id: int
    username: str
    email: EmailStr

    model_config = {"from_attributes": True}


class UserOutSchema(UserReadSchema):
    """Schema for signup/profile responses."""
    pass


class TokenSchema(BaseModel):
    """Schema for authentication response (login)."""
    access_token: str
    token_type: str = "bearer"


T = TypeVar("T")


class CursorPage(BaseModel, Generic[T]):
    """Generic cursor pagination response."""
    total: int
    items: List[T]
    next_cursor: Optional[int] = None


class UserCursorPage(CursorPage[UserOutSchema]):
    """Cursor-based pagination for Users."""
    items: List[UserOutSchema]

