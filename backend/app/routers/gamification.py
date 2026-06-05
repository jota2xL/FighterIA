"""
Module: routers.gamification
Description: Badges, rankings and streak shield management endpoints
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.gamification import Badge, UserBadge
from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.gamification import (
    BadgeResponse,
    UserBadgeResponse,
    RankingItem,
    RankingResponse,
    ShieldResponse,
)
from app.services import auth_service, gamification_service

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/badges", response_model=List[BadgeResponse])
def list_all_badges(
    db: Session  = Depends(get_db),
    _            = Depends(auth_service.get_current_user),
):
    """Return the full badge catalog (all badges, regardless of user progress)."""
    return db.query(Badge).order_by(Badge.id).all()


@router.get("/me/badges", response_model=List[UserBadgeResponse])
def list_my_badges(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Return only the badges earned by the current user."""
    earned = (
        db.query(UserBadge)
        .filter(UserBadge.user_id == current_user.id)
        .order_by(UserBadge.earned_at.desc())
        .all()
    )
    return [
        UserBadgeResponse(
            badge_id=ub.badge_id,
            display_name=ub.badge.display_name,
            icon_name=ub.badge.icon_name,
            level=ub.badge.level,
            xp_reward=ub.badge.xp_reward,
            earned_at=ub.earned_at,
        )
        for ub in earned
    ]


@router.get("/ranking", response_model=RankingResponse)
def get_ranking(
    page: int                   = Query(1, ge=1),
    limit: int                  = Query(50, ge=1, le=100),
    discipline_id: Optional[int] = Query(None, description="Rank by average score in a specific discipline"),
    db: Session                 = Depends(get_db),
    current_user                = Depends(auth_service.get_current_user),
):
    """
    Return the global leaderboard sorted by XP (or average score if discipline_id provided).
    Also returns the current user's rank.
    """
    if discipline_id:
        # Rank by average score in the given discipline
        subq = (
            db.query(
                Analysis.user_id.label("uid"),
                func.avg(Analysis.global_score).label("avg_score"),
            )
            .join("technique")
            .filter(
                Analysis.status == "completed",
                Analysis.global_score.isnot(None),
            )
            .group_by(Analysis.user_id)
            .subquery()
        )
        ranked_users = (
            db.query(User, subq.c.avg_score)
            .join(subq, User.id == subq.c.uid)
            .filter(User.is_active == True)
            .order_by(subq.c.avg_score.desc())
            .all()
        )
        total = len(ranked_users)
        my_rank = next(
            (i + 1 for i, (u, _) in enumerate(ranked_users) if u.id == current_user.id),
            None,
        )
        page_users = ranked_users[(page - 1) * limit : page * limit]
        items = [
            RankingItem(
                rank=(page - 1) * limit + i + 1,
                user_id=u.id,
                username=u.username,
                full_name=u.full_name,
                belt_level=u.belt_level,
                xp=u.xp or 0,
                average_score=round(avg, 1) if avg else None,
                avatar_url=u.avatar_url,
            )
            for i, (u, avg) in enumerate(page_users)
        ]
    else:
        # Global ranking by XP
        total = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
        all_ranked = (
            db.query(User)
            .filter(User.is_active == True)
            .order_by(User.xp.desc())
            .all()
        )
        my_rank = next(
            (i + 1 for i, u in enumerate(all_ranked) if u.id == current_user.id),
            None,
        )
        page_users = all_ranked[(page - 1) * limit : page * limit]
        items = [
            RankingItem(
                rank=(page - 1) * limit + i + 1,
                user_id=u.id,
                username=u.username,
                full_name=u.full_name,
                belt_level=u.belt_level,
                xp=u.xp or 0,
                average_score=None,
                avatar_url=u.avatar_url,
            )
            for i, u in enumerate(page_users)
        ]

    return RankingResponse(items=items, my_rank=my_rank, total_users=total)


@router.post("/me/buy-shield", response_model=ShieldResponse)
def buy_streak_shield(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Spend 100 XP to add one streak shield to the user's account."""
    return gamification_service.buy_shield(current_user, db)


@router.post("/me/use-shield", response_model=ShieldResponse)
def use_streak_shield(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Activate a streak shield to protect today's streak from resetting."""
    return gamification_service.use_shield(current_user, db)
