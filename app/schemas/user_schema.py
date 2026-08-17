from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


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
    """Schema for updating user profile details."""
    username: Optional[str] = Field(None, min_length=3, max_length=80)
    display_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)

    @field_validator("display_name", "bio", "phone", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and not v.strip():
            return None
        return v


class PasswordChangeSchema(BaseModel):
    """Schema for changing password."""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


class UserReadSchema(BaseModel):
    """Schema for reading user data."""
    id: int
    username: str
    email: EmailStr
    display_name: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

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
