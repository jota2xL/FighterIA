"""
Module: schemas.analysis
Description: Pydantic schemas for analysis creation, detail responses, comparison and comments
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TechniqueMinimal(BaseModel):
    id: int
    name: str
    display_name: str
    discipline_name: str
    difficulty: str

    model_config = {"from_attributes": True}


class JointResultSchema(BaseModel):
    joint_name: str
    measured_angle: float
    reference_min: float
    reference_max: float
    optimal_angle: float
    is_correct: bool
    deviation: float

    model_config = {"from_attributes": True}


class FeedbackItemSchema(BaseModel):
    priority_order: int
    correction_title: str
    correction_text: str
    biomechanical_explanation: Optional[str] = None
    exercise_suggestion: Optional[str] = None
    impact_score: float

    model_config = {"from_attributes": True}


class NewlyEarnedBadge(BaseModel):
    badge_id: int
    display_name: str
    xp_reward: int


class AnalysisDetailResponse(BaseModel):
    id: int
    status: str
    technique: Optional[TechniqueMinimal] = None
    global_score: Optional[float] = None
    power_score: Optional[float] = None
    balance_score: Optional[float] = None
    alignment_score: Optional[float] = None
    speed_score: Optional[float] = None
    xp_awarded: int = 0
    belt_upgraded: bool = False
    new_belt: Optional[str] = None
    newly_earned_badges: List[NewlyEarnedBadge] = []
    joint_results: List[JointResultSchema] = []
    feedback: List[FeedbackItemSchema] = []
    video_overlay_url: Optional[str] = None
    video_original_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    technique_display_name: str
    discipline_name: str
    global_score: Optional[float] = None
    status: str
    video_overlay_url: Optional[str] = None
    created_at: datetime


class AnalysisListResponse(BaseModel):
    items: List[AnalysisListItem]
    total: int
    page: int
    limit: int
    pages: int


class CompareResponse(BaseModel):
    analysis_1: AnalysisDetailResponse
    analysis_2: AnalysisDetailResponse
    score_difference: float
    improved_joints: List[str]
    regressed_joints: List[str]
    improved: bool


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=5, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    content: str
    author_username: str
    author_avatar_url: Optional[str] = None
    created_at: datetime
