"""
Module: services.gamification_service
Description: XP awards, belt progression, daily streak management and badge unlocking
"""
from __future__ import annotations

from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.gamification import Badge, UserBadge
from app.models.analysis import Analysis
from app.models.discipline import Technique, Discipline

# ── Belt thresholds (XP required to reach each belt) ─────────────────────
BELT_THRESHOLDS: dict[str, int] = {
    "blanco":  0,
    "amarillo": 501,
    "naranja": 1501,
    "verde":   3001,
    "azul":    5001,
    "marron":  8001,
    "negro":   12001,
}
BELT_ORDER = list(BELT_THRESHOLDS.keys())

# ── XP reward table (global_score range → base XP) ───────────────────────
XP_TABLE: list[tuple[int, int, int]] = [
    (0,   49,  10),
    (50,  74,  20),
    (75,  89,  30),
    (90,  99,  45),
    (100, 100, 60),
]

# ── Shield cost ───────────────────────────────────────────────────────────
SHIELD_COST_XP = 100


def calculate_xp_reward(global_score: float, xp_multiplier: float) -> int:
    """Return the XP to award for a completed analysis."""
    score = round(global_score)
    base_xp = 10  # minimum
    for low, high, xp in XP_TABLE:
        if low <= score <= high:
            base_xp = xp
            break
    return max(1, round(base_xp * xp_multiplier))


def get_belt_for_xp(xp: int) -> str:
    """Return the belt name corresponding to the given XP total."""
    belt = "blanco"
    for belt_name, threshold in BELT_THRESHOLDS.items():
        if xp >= threshold:
            belt = belt_name
    return belt


def get_next_belt_info(belt_level: str) -> tuple[str | None, int | None]:
    """Return (next_belt_name, xp_required) or (None, None) if at max belt."""
    try:
        idx = BELT_ORDER.index(belt_level)
    except ValueError:
        return None, None
    if idx >= len(BELT_ORDER) - 1:
        return None, None
    next_belt = BELT_ORDER[idx + 1]
    return next_belt, BELT_THRESHOLDS[next_belt]


def award_xp_and_update_belt(user: User, xp_to_add: int, db: Session) -> dict:
    """
    Add XP to user, recalculate belt level.
    Returns {xp_added, new_belt, belt_upgraded}.
    Caller must commit after calling this function.
    """
    old_belt = user.belt_level
    user.xp = (user.xp or 0) + xp_to_add
    new_belt = get_belt_for_xp(user.xp)
    user.belt_level = new_belt
    db.flush()
    return {
        "xp_added": xp_to_add,
        "new_belt": new_belt,
        "belt_upgraded": new_belt != old_belt,
    }


def update_streak(user: User, db: Session) -> None:
    """
    Update the user's training streak based on today's date.
    Rules:
    - Same day as last activity → no change
    - Consecutive day → increment streak
    - Gap of exactly 1 day with shield active → consume shield, keep streak
    - Any other gap → reset to 1
    Caller must commit after calling this function.
    """
    today = date.today()

    if user.last_activity_date is None:
        user.current_streak = 1
    elif user.last_activity_date == today:
        return  # already logged today
    elif user.last_activity_date == today - timedelta(days=1):
        user.current_streak = (user.current_streak or 0) + 1
    else:
        # Missed one or more days
        if user.streak_shield_active:
            user.streak_shield_active = False  # consume the shield, keep the streak
        else:
            user.current_streak = 1  # reset

    user.last_activity_date = today
    if (user.current_streak or 0) > (user.max_streak or 0):
        user.max_streak = user.current_streak
    db.flush()


def buy_shield(user: User, db: Session) -> dict:
    """Spend SHIELD_COST_XP to add one streak shield. Returns updated state."""
    if user.xp < SHIELD_COST_XP:
        from fastapi import HTTPException
        raise HTTPException(400, f"XP insuficiente. Necesitas {SHIELD_COST_XP} XP para comprar un escudo.")
    user.xp -= SHIELD_COST_XP
    user.streak_shields = (user.streak_shields or 0) + 1
    db.commit()
    db.refresh(user)
    return {
        "message": "Escudo de racha comprado",
        "shields_remaining": user.streak_shields,
        "xp_remaining": user.xp,
    }


def use_shield(user: User, db: Session) -> dict:
    """Activate a streak shield for today."""
    if not user.streak_shields:
        from fastapi import HTTPException
        raise HTTPException(400, "No tienes escudos de racha disponibles.")
    user.streak_shields -= 1
    user.streak_shield_active = True
    db.commit()
    db.refresh(user)
    return {
        "message": "Escudo activado para hoy",
        "shields_remaining": user.streak_shields,
        "streak_protected": True,
    }


def check_and_award_badges(user: User, db: Session) -> list[dict]:
    """
    Evaluate all badge conditions for the user and award any newly earned badges.
    Returns a list of newly earned badge dicts: [{badge_id, display_name, xp_reward}].
    Caller must commit after calling this function.
    """
    all_badges = db.query(Badge).all()
    earned_ids = {
        ub.badge_id
        for ub in db.query(UserBadge).filter(UserBadge.user_id == user.id).all()
    }
    newly_earned: list[dict] = []

    for badge in all_badges:
        if badge.id in earned_ids:
            continue
        if _evaluate_condition(badge.condition_type, badge.condition_value, user, db):
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            user.xp = (user.xp or 0) + badge.xp_reward
            db.flush()
            newly_earned.append(
                {
                    "badge_id": badge.id,
                    "display_name": badge.display_name,
                    "xp_reward": badge.xp_reward,
                }
            )

    return newly_earned


def _evaluate_condition(
    condition_type: str, condition_value: int, user: User, db: Session
) -> bool:
    """Return True if the user satisfies the badge condition."""
    if condition_type == "first_analysis":
        return (
            db.query(func.count(Analysis.id))
            .filter(Analysis.user_id == user.id, Analysis.status == "completed")
            .scalar()
            or 0
        ) >= condition_value

    if condition_type == "streak_7":
        return (user.current_streak or 0) >= condition_value

    if condition_type == "score_100":
        return (
            db.query(func.count(Analysis.id))
            .filter(
                Analysis.user_id == user.id,
                Analysis.global_score >= 100.0,
            )
            .scalar()
            or 0
        ) >= 1

    if condition_type in ("muay_thai_50", "bjj_50", "boxing_50"):
        discipline_map = {
            "muay_thai_50": "muay_thai",
            "bjj_50":       "bjj",
            "boxing_50":    "boxing",
        }
        disc_name = discipline_map[condition_type]
        count = (
            db.query(func.count(Analysis.id))
            .join(Technique, Analysis.technique_id == Technique.id)
            .join(Discipline, Technique.discipline_id == Discipline.id)
            .filter(
                Analysis.user_id == user.id,
                Analysis.status == "completed",
                Discipline.name == disc_name,
            )
            .scalar()
            or 0
        )
        return count >= condition_value

    if condition_type == "belt_negro":
        return user.belt_level == "negro"

    # Unknown condition type — never award
    return False
