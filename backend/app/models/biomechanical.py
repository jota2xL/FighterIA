"""
Module: models.biomechanical
Description: Biomechanical reference angles per joint per technique.
             These are the ground-truth values used to evaluate user technique.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class BiomechanicalReference(Base):
    __tablename__ = "biomechanical_references"

    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(Integer, ForeignKey("techniques.id"), nullable=False, index=True)
    joint_name = Column(String(50), nullable=False)
    phase = Column(String(30), default="execution", nullable=False)  # execution | final_position
    min_angle = Column(Float, nullable=False)
    max_angle = Column(Float, nullable=False)
    optimal_angle = Column(Float, nullable=False)
    weight = Column(Float, default=1.0, nullable=False)   # importance in scoring (higher = more weight)
    description = Column(Text, nullable=True)

    technique = relationship("Technique", back_populates="biomechanical_refs")
