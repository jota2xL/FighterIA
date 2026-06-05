"""
Module: routers.auth
Description: Authentication endpoints — register, login, token refresh, password recovery and profile
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from jose import JWTError
import pathlib

from app.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    ForgotPasswordRequest,
    TokenResponse,
    RefreshTokenResponse,
    MessageResponse,
)
from app.schemas.user import UserResponse, UserUpdate
from app.services import auth_service, user_service
from app.utils.security import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account and return JWT tokens."""
    if user_service.get_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Este email ya está registrado.")
    if user_service.get_by_username(db, payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Este nombre de usuario ya está en uso.")
    user = user_service.create(db, payload)
    access  = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email/password and return JWT tokens."""
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email o contraseña incorrectos.")
    access  = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new token pair."""
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token inválido.")
        user = user_service.get_by_id(db, int(data["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuario no encontrado.")
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token de refresco inválido o expirado.")

    access  = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return RefreshTokenResponse(access_token=access, refresh_token=refresh)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest):
    """
    Trigger password recovery flow.
    Always returns 200 regardless of whether the email exists (prevents user enumeration).
    Email sending is mocked — no real email is sent.
    """
    return MessageResponse(
        message="Si este email está registrado, recibirás instrucciones en breve."
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(auth_service.get_current_user)):
    """Return the full profile of the currently authenticated user."""
    return current_user
