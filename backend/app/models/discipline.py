"""
Module: models.discipline
Description: Discipline and Technique catalog models — populated by seed, read-only at runtime
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)          # muay_thai | bjj | boxing
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)

    techniques = relationship("Technique", back_populates="discipline", lazy="select")


class Technique(Base):
    __tablename__ = "techniques"

    id = Column(Integer, primary_key=True, index=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium", nullable=False)  # easy | medium | hard
    xp_multiplier = Column(Float, default=1.0, nullable=False)

    discipline = relationship("Discipline", back_populates="techniques")
    biomechanical_refs = relationship("BiomechanicalReference", back_populates="technique", lazy="select")
    analyses = relationship("Analysis", back_populates="technique", lazy="select")
