"""
Module: schemas.dashboard
Description: Pydantic schemas for dashboard summary, progress chart and activity heatmap
"""
from pydantic import BaseModel
from typing import Optional, List


class RecentBadge(BaseModel):
    badge_id: int
    display_name: str
    icon_name: str
    level: str
    earned_at: str


class RecentAnalysis(BaseModel):
    id: int
    technique_display_name: str
    discipline_name: str
    global_score: Optional[float]
    created_at: str


class DashboardResponse(BaseModel):
    total_analyses: int
    best_score: Optional[float]
    average_score: Optional[float]
    favorite_discipline: Optional[str]
    most_analyzed_technique: Optional[str]
    xp: int
    belt_level: str
    xp_for_next_belt: Optional[int]
    xp_next_belt_name: Optional[str]
    current_streak: int
    max_streak: int
    streak_shields: int
    recent_badges: List[RecentBadge]
    recent_analyses: List[RecentAnalysis]


class ProgressDataset(BaseModel):
    discipline: str
    discipline_id: int
    color: str
    data: List[Optional[float]]


class ProgressResponse(BaseModel):
    labels: List[str]
    datasets: List[ProgressDataset]


class HeatmapEntry(BaseModel):
    date: str
    count: int


class HeatmapResponse(BaseModel):
    data: List[HeatmapEntry]
