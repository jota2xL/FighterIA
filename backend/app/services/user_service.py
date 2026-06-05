"""
Module: services.user_service
Description: User CRUD operations and profile management including avatar upload
"""
import json
import pathlib
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.auth import RegisterRequest
from app.schemas.user import UserUpdate, PublicUserResponse
from app.utils.security import hash_password
from app.utils.storage import get_avatar_path

ALLOWED_AVATAR_TYPES = {".jpg", ".jpeg", ".png", ".webp"}
MAX_AVATAR_SIZE_BYTES = 2 * 1024 * 1024  # 2 MB


def get_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create(db: Session, payload: RegisterRequest) -> User:
    """Create a new user record. Caller must check for duplicate email/username first."""
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        account_type=payload.account_type,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(
    db: Session,
    user: User,
    data: UserUpdate,
    avatar_bytes: bytes | None = None,
    avatar_extension: str | None = None,
) -> User:
    """
    Update mutable profile fields. Handles avatar file upload.
    avatar_extension must include the leading dot if provided, e.g. '.jpg'
    """
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field == "disciplines" and isinstance(value, str):
            # Validate it is valid JSON before storing
            try:
                json.loads(value)
            except (json.JSONDecodeError, TypeError):
                value = "[]"
        setattr(user, field, value)

    if avatar_bytes is not None and avatar_extension is not None:
        if avatar_extension.lower() not in ALLOWED_AVATAR_TYPES:
            from fastapi import HTTPException
            raise HTTPException(400, "Formato de imagen no soportado. Usa JPG, PNG o WebP.")
        if len(avatar_bytes) > MAX_AVATAR_SIZE_BYTES:
            from fastapi import HTTPException
            raise HTTPException(400, "La imagen supera los 2MB permitidos.")
        avatar_path = get_avatar_path(user.id, avatar_extension.lower())
        avatar_path.write_bytes(avatar_bytes)
        user.avatar_url = f"/storage/avatars/avatar_{user.id}{avatar_extension.lower()}"

    db.commit()
    db.refresh(user)
    return user


def get_public_profile(db: Session, user_id: int) -> PublicUserResponse | None:
    """Return a public profile with aggregated stats."""
    user = get_by_id(db, user_id)
    if not user:
        return None

    stats = db.query(
        func.count(Analysis.id).label("total"),
        func.max(Analysis.global_score).label("best"),
        func.avg(Analysis.global_score).label("avg"),
    ).filter(
        Analysis.user_id == user_id,
        Analysis.status == "completed",
    ).first()

    return PublicUserResponse(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        account_type=user.account_type,
        bio=user.bio,
        gym=user.gym,
        belt_level=user.belt_level,
        xp=user.xp,
        current_streak=user.current_streak,
        avatar_url=user.avatar_url,
        total_analyses=stats.total or 0,
        best_score=round(stats.best, 1) if stats.best else None,
        average_score=round(stats.avg, 1) if stats.avg else None,
    )
