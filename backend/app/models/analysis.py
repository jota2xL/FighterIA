"""
Module: models.analysis
Description: Analysis (video processing record), joint measurement results,
             prioritized feedback and instructor comments
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    technique_id = Column(Integer, ForeignKey("techniques.id"), nullable=False)
    video_original_path = Column(String(500), nullable=False)
    video_overlay_path = Column(String(500), nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending|processing|completed|failed
    global_score = Column(Float, nullable=True)
    power_score = Column(Float, nullable=True)
    balance_score = Column(Float, nullable=True)
    alignment_score = Column(Float, nullable=True)
    speed_score = Column(Float, nullable=True)
    xp_awarded = Column(Integer, default=0, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="analyses")
    technique = relationship("Technique", back_populates="analyses")
    joint_results = relationship(
        "AnalysisJointResult",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select"
    )
    feedback = relationship(
        "AnalysisFeedback",
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="AnalysisFeedback.priority_order",
        lazy="select"
    )
    comments = relationship(
        "AnalysisComment",
        back_populates="analysis",
        cascade="all, delete-orphan",
        lazy="select"
    )


class AnalysisJointResult(Base):
    __tablename__ = "analysis_joint_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    joint_name = Column(String(50), nullable=False)
    measured_angle = Column(Float, nullable=False)
    reference_min = Column(Float, nullable=False)
    reference_max = Column(Float, nullable=False)
    optimal_angle = Column(Float, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    deviation = Column(Float, nullable=False)  # measured_angle - optimal_angle

    analysis = relationship("Analysis", back_populates="joint_results")


class AnalysisFeedback(Base):
    __tablename__ = "analysis_feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    correction_title = Column(String(200), nullable=False)
    correction_text = Column(Text, nullable=False)
    biomechanical_explanation = Column(Text, nullable=True)
    exercise_suggestion = Column(Text, nullable=True)
    priority_order = Column(Integer, nullable=False)   # 1 = highest impact
    impact_score = Column(Float, nullable=False)       # 0.0 – 1.0

    analysis = relationship("Analysis", back_populates="feedback")


class AnalysisComment(Base):
    __tablename__ = "analysis_comments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    analysis = relationship("Analysis", back_populates="comments")
    author = relationship("User")
