"""
Module: routers.crm
Description: CRM endpoints — Gym, Trainer and Lead CRUD plus gym metrics.
             All endpoints require JWT authentication.
             Prefix: /crm | Tags: ["CRM"]
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.crm import (
    GymCreate, GymUpdate, GymOut,
    TrainerCreate, TrainerUpdate, TrainerOut,
    LeadCreate, LeadUpdate, LeadOut,
    GymMetricsResponse,
)
from app.services import crm_service
from app.services import auth_service

router = APIRouter(prefix="/crm", tags=["CRM"])


# ══════════════════════════════════════════════════════════════════════════════
#  GYMS
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/gyms", response_model=GymOut, status_code=status.HTTP_201_CREATED)
def create_gym(
    payload:      GymCreate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Create a new gym record."""
    return crm_service.create_gym(db, payload)


@router.get("/gyms", response_model=List[GymOut])
def list_gyms(
    page:         int     = Query(1, ge=1),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return a paginated list of all gyms."""
    skip = (page - 1) * limit
    return crm_service.list_gyms(db, skip=skip, limit=limit)


@router.get("/gyms/{gym_id}", response_model=GymOut)
def get_gym(
    gym_id:       int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return detail of a single gym by ID."""
    return crm_service.get_gym(db, gym_id)


@router.put("/gyms/{gym_id}", response_model=GymOut)
def update_gym(
    gym_id:       int,
    payload:      GymUpdate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Update fields of an existing gym."""
    return crm_service.update_gym(db, gym_id, payload)


@router.delete("/gyms/{gym_id}")
def delete_gym(
    gym_id:       int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Delete a gym and all its associated trainers and leads."""
    crm_service.delete_gym(db, gym_id)
    return {"deleted": True}


@router.get("/gyms/{gym_id}/metrics", response_model=GymMetricsResponse)
def get_gym_metrics(
    gym_id:       int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return aggregated metrics for a gym: trainer count, lead count, conversion rate."""
    return crm_service.get_gym_metrics(db, gym_id)


# ══════════════════════════════════════════════════════════════════════════════
#  TRAINERS (nested under gym)
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/gyms/{gym_id}/trainers",
    response_model=TrainerOut,
    status_code=status.HTTP_201_CREATED,
)
def create_trainer(
    gym_id:       int,
    payload:      TrainerCreate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Assign a new trainer to a gym."""
    # Override payload gym_id with the path parameter for safety
    payload_dict = payload.model_dump()
    payload_dict["gym_id"] = gym_id
    from app.schemas.crm import TrainerCreate as TC
    merged = TC(**payload_dict)
    return crm_service.create_trainer(db, merged)


@router.get("/gyms/{gym_id}/trainers", response_model=List[TrainerOut])
def list_gym_trainers(
    gym_id:       int,
    page:         int     = Query(1, ge=1),
    limit:        int     = Query(20, ge=1, le=100),
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return a paginated list of trainers for a specific gym."""
    skip = (page - 1) * limit
    return crm_service.list_trainers(db, gym_id=gym_id, skip=skip, limit=limit)


@router.get("/gyms/{gym_id}/trainers/{trainer_id}", response_model=TrainerOut)
def get_gym_trainer(
    gym_id:       int,
    trainer_id:   int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return detail of a single trainer."""
    return crm_service.get_trainer(db, trainer_id)


@router.put("/gyms/{gym_id}/trainers/{trainer_id}", response_model=TrainerOut)
def update_gym_trainer(
    gym_id:       int,
    trainer_id:   int,
    payload:      TrainerUpdate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Update the role or status of a trainer."""
    return crm_service.update_trainer(db, trainer_id, payload)


@router.delete("/gyms/{gym_id}/trainers/{trainer_id}")
def delete_gym_trainer(
    gym_id:       int,
    trainer_id:   int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Remove a trainer from the gym."""
    crm_service.delete_trainer(db, trainer_id)
    return {"deleted": True}


# ══════════════════════════════════════════════════════════════════════════════
#  LEADS (nested under gym)
# ══════════════════════════════════════════════════════════════════════════════

@router.post(
    "/gyms/{gym_id}/leads",
    response_model=LeadOut,
    status_code=status.HTTP_201_CREATED,
)
def create_lead(
    gym_id:       int,
    payload:      LeadCreate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Register a new sales lead associated with a gym."""
    return crm_service.create_lead(db, gym_id, payload)


@router.get("/gyms/{gym_id}/leads", response_model=List[LeadOut])
def list_gym_leads(
    gym_id:       int,
    lead_status:  Optional[str] = Query(None, alias="status"),
    source:       Optional[str] = Query(None),
    page:         int           = Query(1, ge=1),
    limit:        int           = Query(20, ge=1, le=100),
    db:           Session       = Depends(get_db),
    current_user                = Depends(auth_service.get_current_user),
):
    """Return a filtered, paginated list of leads for a gym."""
    skip = (page - 1) * limit
    return crm_service.list_leads(
        db, gym_id=gym_id, lead_status=lead_status, source=source,
        skip=skip, limit=limit,
    )


@router.get("/gyms/{gym_id}/leads/{lead_id}", response_model=LeadOut)
def get_gym_lead(
    gym_id:       int,
    lead_id:      int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Return detail of a single lead."""
    return crm_service.get_lead(db, lead_id)


@router.put("/gyms/{gym_id}/leads/{lead_id}", response_model=LeadOut)
def update_gym_lead(
    gym_id:       int,
    lead_id:      int,
    payload:      LeadUpdate,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Update data or status of a lead."""
    return crm_service.update_lead(db, lead_id, payload)


@router.delete("/gyms/{gym_id}/leads/{lead_id}")
def delete_gym_lead(
    gym_id:       int,
    lead_id:      int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """Delete a lead record."""
    crm_service.delete_lead(db, lead_id)
    return {"deleted": True}
