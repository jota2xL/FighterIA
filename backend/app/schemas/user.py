"""
Module: schemas.user
Description: Pydantic schemas for user profile responses and profile update requests
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
import json


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    account_type: str
    bio: Optional[str] = None
    gym: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    experience_years: int = 0
    disciplines: List[str] = []
    avatar_url: Optional[str] = None
    xp: int = 0
    belt_level: str = "blanco"
    current_streak: int = 0
    max_streak: int = 0
    streak_shields: int = 0
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("disciplines", mode="before")
    @classmethod
    def parse_disciplines(cls, v: Any) -> List[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []


class PublicUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    account_type: str
    bio: Optional[str] = None
    gym: Optional[str] = None
    belt_level: str
    xp: int
    current_streak: int
    avatar_url: Optional[str] = None
    total_analyses: int = 0
    best_score: Optional[float] = None
    average_score: Optional[float] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    gym: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    experience_years: Optional[int] = Field(None, ge=0, le=100)
    disciplines: Optional[str] = None  # JSON array as string from multipart form
