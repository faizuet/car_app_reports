from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import config


ALGORITHM = config.ALGORITHM
SECRET_KEY = config.JWT_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token extraction dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Security:
    """Handles password hashing and JWT token operations."""

    # Password utilities
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return pwd_context.verify(plain, hashed)

    # Token utilities
    @staticmethod
    def create_access_token(subject: str, minutes: Optional[int] = None) -> str:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=minutes or ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload = {"sub": subject, "exp": expires, "type": "access"}
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            return None


security = Security()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Decode a JWT token and return its payload.
    Works as a FastAPI dependency for routes.
    """
    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

