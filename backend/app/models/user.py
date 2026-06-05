"""
Module: models.user
Description: User model — authentication, profile, gamification state and streak tracking
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False, default="alumno")  # alumno | instructor
    bio = Column(String(500), nullable=True)
    gym = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    experience_years = Column(Integer, default=0, nullable=False)
    disciplines = Column(String(255), nullable=True)  # JSON array stored as string: '["boxing","bjj"]'
    avatar_url = Column(String(500), nullable=True)

    # Gamification
    xp = Column(Integer, default=0, nullable=False)
    belt_level = Column(String(20), default="blanco", nullable=False)

    # Streak
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    streak_shield_active = Column(Boolean, default=False, nullable=False)
    streak_shields = Column(Integer, default=0, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    analyses = relationship("Analysis", back_populates="user", lazy="select")
    user_badges = relationship("UserBadge", back_populates="user", lazy="select")
    instructor_groups = relationship("InstructorGroup", back_populates="instructor", lazy="select")
    group_memberships = relationship("GroupMember", back_populates="student", lazy="select")
