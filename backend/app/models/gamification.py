"""
Module: models.gamification
Description: Badge catalog and user-badge junction table for the achievement system
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)      # internal key: 'first_analysis'
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(20), nullable=False)                   # bronze | silver | gold
    icon_name = Column(String(50), nullable=False)
    condition_type = Column(String(50), nullable=False)          # 'first_analysis', 'streak_7', ...
    condition_value = Column(Integer, default=1, nullable=False)
    xp_reward = Column(Integer, default=50, nullable=False)

    user_badges = relationship("UserBadge", back_populates="badge", lazy="select")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
    )

    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
