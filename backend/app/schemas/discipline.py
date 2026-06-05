"""
Module: schemas.discipline
Description: Pydantic schemas for discipline and technique catalog responses
"""
from pydantic import BaseModel
from typing import Optional


class DisciplineResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TechniqueResponse(BaseModel):
    id: int
    discipline_id: int
    name: str
    display_name: str
    description: Optional[str] = None
    difficulty: str
    xp_multiplier: float

    model_config = {"from_attributes": True}
