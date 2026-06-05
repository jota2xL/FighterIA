"""
Module: services.dashboard_service
Description: Aggregated statistics, progress chart data and activity heatmap for the dashboard
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis import Analysis
from app.models.discipline import Technique, Discipline
from app.models.gamification import UserBadge
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse,
    HeatmapEntry,
    HeatmapResponse,
    ProgressDataset,
    ProgressResponse,
    RecentAnalysis,
    RecentBadge,
)
from app.services.gamification_service import BELT_THRESHOLDS, BELT_ORDER

DISCIPLINE_COLORS = {
    "Muay Thai": "#dc2626",
    "BJJ":       "#d4af37",
    "Boxeo":     "#2563eb",
}


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    """Build the full dashboard summary for a user."""
    # All completed analyses
    completed = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id, Analysis.status == "completed")
        .all()
    )
    total = len(completed)
    best  = max((a.global_score for a in completed if a.global_score is not None), default=None)
    avg   = (
        round(sum(a.global_score for a in completed if a.global_score) / total, 1)
        if total
        else None
    )

    # Favourite discipline and most-analysed technique
    disc_counts: dict[str, int] = defaultdict(int)
    tech_counts: dict[str, int] = defaultdict(int)
    for a in completed:
        if a.technique:
            disc_counts[a.technique.discipline.display_name] += 1
            tech_counts[a.technique.display_name] += 1

    fav_disc = max(disc_counts, key=disc_counts.get) if disc_counts else None
    fav_tech = max(tech_counts, key=tech_counts.get) if tech_counts else None

    # Next belt info
    try:
        belt_idx = BELT_ORDER.index(user.belt_level)
    except ValueError:
        belt_idx = 0
    next_belt     = BELT_ORDER[belt_idx + 1] if belt_idx < len(BELT_ORDER) - 1 else None
    xp_for_next   = BELT_THRESHOLDS[next_belt] if next_belt else None
    next_belt_name = next_belt

    # Recent badges (last 5)
    recent_ubs = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == user.id)
        .order_by(UserBadge.earned_at.desc())
        .limit(5)
        .all()
    )
    recent_badges = [
        RecentBadge(
            badge_id=ub.badge_id,
            display_name=ub.badge.display_name,
            icon_name=ub.badge.icon_name,
            level=ub.badge.level,
            earned_at=ub.earned_at.isoformat(),
        )
        for ub in recent_ubs
    ]

    # Recent analyses (last 3)
    recent_analyses_orm = (
        db.query(Analysis)
        .filter(Analysis.user_id == user.id, Analysis.status == "completed")
        .order_by(Analysis.created_at.desc())
        .limit(3)
        .all()
    )
    recent_analyses = [
        RecentAnalysis(
            id=a.id,
            technique_display_name=a.technique.display_name if a.technique else "—",
            discipline_name=(
                a.technique.discipline.display_name
                if a.technique and a.technique.discipline
                else "—"
            ),
            global_score=a.global_score,
            created_at=a.created_at.isoformat(),
        )
        for a in recent_analyses_orm
    ]

    return DashboardResponse(
        total_analyses=total,
        best_score=best,
        average_score=avg,
        favorite_discipline=fav_disc,
        most_analyzed_technique=fav_tech,
        xp=user.xp or 0,
        belt_level=user.belt_level,
        xp_for_next_belt=xp_for_next,
        xp_next_belt_name=next_belt_name,
        current_streak=user.current_streak or 0,
        max_streak=user.max_streak or 0,
        streak_shields=user.streak_shields or 0,
        recent_badges=recent_badges,
        recent_analyses=recent_analyses,
    )


def get_progress(
    db: Session,
    user_id: int,
    discipline_id: Optional[int] = None,
    days: int = 30,
) -> ProgressResponse:
    """Return weekly average scores grouped by day for a progress line chart."""
    cutoff = date.today() - timedelta(days=days)

    query = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.status == "completed",
        Analysis.created_at >= cutoff,
        Analysis.global_score.isnot(None),
    )
    if discipline_id:
        query = query.join(Technique, Analysis.technique_id == Technique.id).filter(
            Technique.discipline_id == discipline_id
        )

    analyses = query.order_by(Analysis.created_at).all()

    # Group by ISO date string
    daily: dict[str, list[float]] = defaultdict(list)
    for a in analyses:
        day_label = a.created_at.strftime("%Y-%m-%d")
        if a.global_score is not None:
            daily[day_label].append(a.global_score)

    labels = sorted(daily.keys())
    data   = [round(sum(daily[l]) / len(daily[l]), 1) for l in labels]

    # Determine discipline label and color
    if discipline_id:
        disc = db.query(Discipline).filter(Discipline.id == discipline_id).first()
        disc_name = disc.display_name if disc else "Todas"
    else:
        disc_name = "Todas"

    color = DISCIPLINE_COLORS.get(disc_name, "#dc2626")

    return ProgressResponse(
        labels=labels,
        datasets=[
            ProgressDataset(
                discipline=disc_name,
                discipline_id=discipline_id or 0,
                color=color,
                data=data,
            )
        ],
    )


def get_heatmap(db: Session, user_id: int) -> HeatmapResponse:
    """Return per-day analysis counts for the last 90 days."""
    cutoff = date.today() - timedelta(days=90)

    rows = (
        db.query(
            func.date(Analysis.created_at).label("day"),
            func.count(Analysis.id).label("count"),
        )
        .filter(
            Analysis.user_id == user_id,
            Analysis.status == "completed",
            Analysis.created_at >= cutoff,
        )
        .group_by(func.date(Analysis.created_at))
        .all()
    )

    return HeatmapResponse(
        data=[HeatmapEntry(date=str(r.day), count=r.count) for r in rows]
    )
