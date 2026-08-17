import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from app.core.config import config

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def ensure_upload_dir() -> Path:
    path = Path(config.UPLOAD_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_avatar(user_id: int, file: UploadFile) -> str:
    """Save avatar file and return relative URL path."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG, PNG, WebP, and GIF images are allowed",
        )

    content = file.file.read()
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be smaller than 5 MB",
        )

    ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }[file.content_type]

    upload_dir = ensure_upload_dir() / "avatars"
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = f"user_{user_id}_{uuid.uuid4().hex}{ext}"
    filepath = upload_dir / filename
    filepath.write_bytes(content)

    return f"/uploads/avatars/{filename}"


def delete_avatar_file(profile_image: str | None) -> None:
    """Remove avatar file from disk if it exists."""
    if not profile_image or not profile_image.startswith("/uploads/"):
        return
    relative = profile_image.removeprefix("/uploads/")
    filepath = Path(config.UPLOAD_DIR) / relative
    if filepath.exists():
        filepath.unlink()
