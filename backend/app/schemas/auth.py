"""
Module: schemas.auth
Description: Pydantic schemas for registration, login, token responses and password recovery
"""
from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    account_type: str = Field(..., pattern=r"^(alumno|instructor)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
