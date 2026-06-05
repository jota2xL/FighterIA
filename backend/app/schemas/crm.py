"""
Module: schemas.crm
Description: Pydantic v2 schemas for CRM module (Gym, Trainer, Lead) and metrics endpoint
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ── Gym ───────────────────────────────────────────────────────────────────────

class GymCreate(BaseModel):
    name:    str            = Field(..., min_length=2, max_length=150)
    city:    Optional[str]  = None
    country: Optional[str]  = None
    plan:    str            = Field(default="free", pattern="^(free|pro|enterprise)$")


class GymUpdate(BaseModel):
    name:    Optional[str] = Field(None, min_length=2, max_length=150)
    city:    Optional[str] = None
    country: Optional[str] = None
    plan:    Optional[str] = Field(None, pattern="^(free|pro|enterprise)$")


class GymOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    name:       str
    city:       Optional[str]
    country:    Optional[str]
    plan:       str
    created_at: datetime


# ── Trainer ───────────────────────────────────────────────────────────────────

class TrainerCreate(BaseModel):
    gym_id:  int
    user_id: Optional[int] = None
    role:    str = Field(default="trainer", pattern="^(trainer|head_coach|admin)$")
    status:  str = Field(default="active", pattern="^(active|inactive|pending)$")


class TrainerUpdate(BaseModel):
    role:   Optional[str] = Field(None, pattern="^(trainer|head_coach|admin)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|pending)$")


class TrainerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:      int
    gym_id:  int
    user_id: Optional[int]
    role:    str
    status:  str


# ── Lead ──────────────────────────────────────────────────────────────────────

class LeadCreate(BaseModel):
    gym_id: Optional[int]  = None
    name:   str            = Field(..., min_length=2, max_length=100)
    email:  EmailStr
    phone:  Optional[str]  = None
    status: str            = Field(default="new",
                                   pattern="^(new|contacted|qualified|converted|lost)$")
    source: Optional[str]  = Field(
        None, pattern="^(manual|web|referral|social|ads)$")
    notes:  Optional[str]  = None


class LeadUpdate(BaseModel):
    name:   Optional[str]      = None
    email:  Optional[EmailStr] = None
    phone:  Optional[str]      = None
    status: Optional[str]      = Field(
        None, pattern="^(new|contacted|qualified|converted|lost)$")
    source: Optional[str]      = None
    notes:  Optional[str]      = None
    gym_id: Optional[int]      = None


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:         int
    gym_id:     Optional[int]
    name:       str
    email:      str
    phone:      Optional[str]
    status:     str
    source:     Optional[str]
    notes:      Optional[str]
    created_at: datetime


# ── Metrics ───────────────────────────────────────────────────────────────────

class GymMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gym_id:             int
    gym_name:           str
    total_trainers:     int
    total_leads:        int
    conversion_rate:    float
    plan:               str
