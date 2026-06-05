"""
Module: schemas.gamification
Description: Pydantic schemas for badges, user achievements, ranking and streak shield operations
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BadgeResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    level: str
    icon_name: str
    xp_reward: int

    model_config = {"from_attributes": True}


class UserBadgeResponse(BaseModel):
    badge_id: int
    display_name: str
    icon_name: str
    level: str
    xp_reward: int
    earned_at: datetime

    model_config = {"from_attributes": True}


class RankingItem(BaseModel):
    rank: int
    user_id: int
    username: str
    full_name: str
    belt_level: str
    xp: int
    average_score: Optional[float] = None
    avatar_url: Optional[str] = None


class RankingResponse(BaseModel):
    items: List[RankingItem]
    my_rank: Optional[int]
    total_users: int


class ShieldResponse(BaseModel):
    message: str
    shields_remaining: int
    xp_remaining: Optional[int] = None
    streak_protected: Optional[bool] = None
