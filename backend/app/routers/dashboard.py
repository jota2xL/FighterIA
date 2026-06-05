"""
Module: routers.dashboard
Description: Personal progress dashboard — summary stats, progress chart and activity heatmap
"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import DashboardResponse, HeatmapResponse, ProgressResponse
from app.services import auth_service, dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me", response_model=DashboardResponse)
def get_dashboard(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Return the aggregated dashboard summary for the current user."""
    return dashboard_service.get_dashboard(db, current_user)


@router.get("/me/progress", response_model=ProgressResponse)
def get_progress(
    discipline_id: Optional[int] = Query(None, description="Filter by discipline ID (null = all)"),
    days: int                    = Query(30, ge=7, le=365),
    db: Session                  = Depends(get_db),
    current_user                 = Depends(auth_service.get_current_user),
):
    """Return daily average scores for a progress line chart."""
    return dashboard_service.get_progress(db, current_user.id, discipline_id, days)


@router.get("/me/heatmap", response_model=HeatmapResponse)
def get_heatmap(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Return per-day analysis counts for the last 90 days (activity heatmap)."""
    return dashboard_service.get_heatmap(db, current_user.id)
