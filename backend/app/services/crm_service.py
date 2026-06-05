"""
Module: services.crm_service
Description: CRUD operations for Gym, Trainer and Lead, plus get_gym_metrics aggregation.
             No authentication logic here — authorization is enforced at the router layer.
"""
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.crm import Gym, Trainer, Lead
from app.schemas.crm import (
    GymCreate, GymUpdate,
    TrainerCreate, TrainerUpdate,
    LeadCreate, LeadUpdate,
    GymMetricsResponse,
)


# ── Revenue constants ─────────────────────────────────────────────────────────

_PLAN_PRICE = {"free": 0.0, "pro": 29.99, "enterprise": 99.99}


# ══════════════════════════════════════════════════════════════════════════════
#  GYM CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_gym(db: Session, payload: GymCreate) -> Gym:
    gym = Gym(
        name=payload.name,
        city=payload.city,
        country=payload.country,
        plan=payload.plan,
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)
    return gym


def get_gym(db: Session, gym_id: int) -> Gym:
    gym = db.query(Gym).filter(Gym.id == gym_id).first()
    if not gym:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Gimnasio no encontrado.")
    return gym


def list_gyms(db: Session, skip: int = 0, limit: int = 20) -> List[Gym]:
    return db.query(Gym).offset(skip).limit(limit).all()


def update_gym(db: Session, gym_id: int, payload: GymUpdate) -> Gym:
    gym = get_gym(db, gym_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(gym, field, value)
    db.commit()
    db.refresh(gym)
    return gym


def delete_gym(db: Session, gym_id: int) -> None:
    gym = get_gym(db, gym_id)
    db.delete(gym)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  TRAINER CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_trainer(db: Session, payload: TrainerCreate) -> Trainer:
    # Ensure the gym exists
    get_gym(db, payload.gym_id)
    trainer = Trainer(
        gym_id=payload.gym_id,
        user_id=payload.user_id,
        role=payload.role,
        status=payload.status,
    )
    db.add(trainer)
    db.commit()
    db.refresh(trainer)
    return trainer


def get_trainer(db: Session, trainer_id: int) -> Trainer:
    trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not trainer:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Trainer no encontrado.")
    return trainer


def list_trainers(
    db: Session,
    gym_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Trainer]:
    query = db.query(Trainer)
    if gym_id is not None:
        query = query.filter(Trainer.gym_id == gym_id)
    return query.offset(skip).limit(limit).all()


def update_trainer(db: Session, trainer_id: int, payload: TrainerUpdate) -> Trainer:
    trainer = get_trainer(db, trainer_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(trainer, field, value)
    db.commit()
    db.refresh(trainer)
    return trainer


def delete_trainer(db: Session, trainer_id: int) -> None:
    trainer = get_trainer(db, trainer_id)
    db.delete(trainer)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  LEAD CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_lead(db: Session, gym_id: int, payload: LeadCreate) -> Lead:
    # Ensure the gym exists when a gym_id is scoped via URL path
    get_gym(db, gym_id)
    lead = Lead(
        gym_id=gym_id,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        status=payload.status,
        source=payload.source or "",
        notes=payload.notes or "",
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def get_lead(db: Session, lead_id: int) -> Lead:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lead no encontrado.")
    return lead


def list_leads(
    db: Session,
    gym_id: Optional[int] = None,
    lead_status: Optional[str] = None,
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> List[Lead]:
    query = db.query(Lead)
    if gym_id is not None:
        query = query.filter(Lead.gym_id == gym_id)
    if lead_status is not None:
        query = query.filter(Lead.status == lead_status)
    if source is not None:
        query = query.filter(Lead.source == source)
    return query.offset(skip).limit(limit).all()


def update_lead(db: Session, lead_id: int, payload: LeadUpdate) -> Lead:
    lead = get_lead(db, lead_id)
    data = payload.model_dump(exclude_unset=True)
    if "email" in data and data["email"] is not None:
        data["email"] = str(data["email"])
    for field, value in data.items():
        setattr(lead, field, value)
    db.commit()
    db.refresh(lead)
    return lead


def delete_lead(db: Session, lead_id: int) -> None:
    lead = get_lead(db, lead_id)
    db.delete(lead)
    db.commit()


# ══════════════════════════════════════════════════════════════════════════════
#  METRICS
# ══════════════════════════════════════════════════════════════════════════════

def get_gym_metrics(db: Session, gym_id: int) -> GymMetricsResponse:
    """
    Aggregate metrics for a single gym:
    - total_trainers: count of Trainer rows for this gym
    - total_leads: count of Lead rows for this gym
    - conversion_rate: percentage of leads with status='converted'
    - plan: current plan of the gym
    """
    gym = get_gym(db, gym_id)

    total_trainers = db.query(Trainer).filter(Trainer.gym_id == gym_id).count()

    total_leads = db.query(Lead).filter(Lead.gym_id == gym_id).count()
    converted_leads = db.query(Lead).filter(
        Lead.gym_id == gym_id,
        Lead.status == "converted",
    ).count()

    conversion_rate = (converted_leads / total_leads * 100.0) if total_leads > 0 else 0.0

    return GymMetricsResponse(
        gym_id=gym.id,
        gym_name=gym.name,
        total_trainers=total_trainers,
        total_leads=total_leads,
        conversion_rate=round(conversion_rate, 2),
        plan=gym.plan,
    )
