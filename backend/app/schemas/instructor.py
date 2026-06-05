"""
Module: schemas.instructor
Description: Pydantic schemas for instructor group management and student progress views
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    member_count: int
    is_active: bool
    created_at: datetime


class GroupMemberSummary(BaseModel):
    student_id: int
    username: str
    full_name: str
    belt_level: str
    xp: int
    total_analyses: int
    last_activity_date: Optional[date]
    average_score: Optional[float]
    joined_at: datetime


class GroupDetailResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    members: List[GroupMemberSummary]


class JoinGroupRequest(BaseModel):
    invite_code: str = Field(..., min_length=4, max_length=20)
