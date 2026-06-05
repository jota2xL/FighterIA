"""
Module: services.auth_service
Description: Authentication helpers and get_current_user / require_instructor
             FastAPI dependencies for route protection
"""
from typing import Optional

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError

from app.database import get_db
from app.models.user import User
from app.utils.security import verify_password, decode_token

_bearer = HTTPBearer()


def authenticate(db: Session, email: str, password: str) -> User | None:
    """
    Validate email/password credentials.
    Returns the User if valid, None otherwise.
    Deliberately returns None for both 'user not found' and 'wrong password'
    to prevent user enumeration.
    """
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency — validates the Bearer token and returns the authenticated User.
    Raises HTTP 401 if the token is missing, invalid or expired.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise exc
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise exc

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise exc
    return user


def get_video_stream_user(
    token: Optional[str] = Query(None, description="JWT access token for video streaming"),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency for video streaming endpoints.
    Reads the JWT from the 'token' query parameter because <video> elements
    cannot send custom headers.  Falls back to the same validation logic as
    get_current_user so the security contract is identical.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise exc
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise exc
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise exc

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise exc
    return user


def require_instructor(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    FastAPI dependency — raises HTTP 403 if the authenticated user is not an instructor.
    Chain after get_current_user.
    """
    if current_user.account_type != "instructor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los instructores pueden acceder a este recurso",
        )
    return current_user
