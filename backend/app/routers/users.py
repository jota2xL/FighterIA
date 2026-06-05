"""
Module: routers.users
Description: User profile update and public profile endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import pathlib

from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate, PublicUserResponse
from app.services import auth_service, user_service

router = APIRouter(prefix="/users", tags=["users"])

ALLOWED_AVATAR_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.put("/me", response_model=UserResponse)
async def update_profile(
    full_name: Optional[str]     = Form(None),
    bio: Optional[str]           = Form(None),
    gym: Optional[str]           = Form(None),
    city: Optional[str]          = Form(None),
    country: Optional[str]       = Form(None),
    experience_years: Optional[int] = Form(None),
    disciplines: Optional[str]   = Form(None),
    avatar: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    """
    Update the current user's profile.
    Accepts multipart/form-data to support optional avatar image upload.
    All fields are optional — only provided fields are updated.
    """
    update_data = UserUpdate(
        full_name=full_name,
        bio=bio,
        gym=gym,
        city=city,
        country=country,
        experience_years=experience_years,
        disciplines=disciplines,
    )

    avatar_bytes: bytes | None = None
    avatar_extension: str | None = None

    if avatar is not None and avatar.filename:
        ext = pathlib.Path(avatar.filename).suffix.lower()
        if ext not in ALLOWED_AVATAR_EXTENSIONS:
            raise HTTPException(400, "Formato de imagen no soportado. Usa JPG, PNG o WebP.")
        avatar_bytes = await avatar.read()
        avatar_extension = ext

    updated = user_service.update_profile(
        db, current_user, update_data, avatar_bytes, avatar_extension
    )
    return UserResponse.model_validate(updated)


@router.get("/{user_id}", response_model=PublicUserResponse)
def get_public_profile(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.get_current_user),
):
    """Return the public profile and aggregated stats of a registered user."""
    profile = user_service.get_public_profile(db, user_id)
    if not profile:
        raise HTTPException(404, "Usuario no encontrado.")
    return profile
