from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Generic, TypeVar

# -------- Input Schemas --------
class UserRegisterSchema(BaseModel):
    """Schema for user registration."""
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


# -------- Output Schemas --------
class UserReadSchema(BaseModel):
    """Base schema for reading user data (id, username, email)."""
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


class UserOutSchema(UserReadSchema):
    """Schema for signup/profile responses (no timestamps)."""
    pass


# -------- Auth Schema --------
class TokenSchema(BaseModel):
    """Schema for authentication response (login)."""
    access_token: str
    token_type: str = "bearer"


# -------- Pagination Schemas --------
T = TypeVar("T")

class CursorPage(BaseModel, Generic[T]):
    """Generic cursor pagination response."""
    total: int
    items: List[T]
    next_cursor: Optional[int] = None


class UserCursorPage(CursorPage[UserOutSchema]):
    """Cursor-based pagination schema for Users."""
    items: List[UserOutSchema]

