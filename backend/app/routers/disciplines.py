"""
Module: routers.disciplines
Description: Read-only endpoints for the discipline and technique catalog
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.discipline import Discipline, Technique
from app.schemas.discipline import DisciplineResponse, TechniqueResponse
from app.services import auth_service

router = APIRouter(prefix="/disciplines", tags=["disciplines"])


@router.get("", response_model=List[DisciplineResponse])
def list_disciplines(
    db: Session = Depends(get_db),
    _=Depends(auth_service.get_current_user),
):
    """Return all disciplines available in the system (populated by seed)."""
    return db.query(Discipline).order_by(Discipline.id).all()


@router.get("/{discipline_id}/techniques", response_model=List[TechniqueResponse])
def list_techniques(
    discipline_id: int,
    db: Session = Depends(get_db),
    _=Depends(auth_service.get_current_user),
):
    """Return all techniques belonging to a specific discipline."""
    discipline = db.query(Discipline).filter(Discipline.id == discipline_id).first()
    if not discipline:
        raise HTTPException(404, "Disciplina no encontrada.")
    return (
        db.query(Technique)
        .filter(Technique.discipline_id == discipline_id)
        .order_by(Technique.id)
        .all()
    )
