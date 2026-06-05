"""
Module: models.crm
Description: CRM models — Gym (tenant), Trainer (staff) and Lead (sales pipeline)
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Gym(Base):
    __tablename__ = "gyms"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(150), nullable=False)
    city       = Column(String(100), nullable=True)
    country    = Column(String(100), nullable=True)
    plan       = Column(String(30), nullable=False, default="free")
    # plan values: "free" | "pro" | "enterprise"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trainers = relationship("Trainer", back_populates="gym", lazy="select")
    leads    = relationship("Lead",    back_populates="gym", lazy="select")


class Trainer(Base):
    __tablename__ = "trainers"

    id      = Column(Integer, primary_key=True, index=True)
    gym_id  = Column(Integer, ForeignKey("gyms.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    role    = Column(String(50), nullable=False, default="trainer")
    # role values: "trainer" | "head_coach" | "admin"
    status  = Column(String(20), nullable=False, default="active")
    # status values: "active" | "inactive" | "pending"

    gym  = relationship("Gym",  back_populates="trainers")
    user = relationship("User", lazy="select")


class Lead(Base):
    __tablename__ = "leads"

    id         = Column(Integer, primary_key=True, index=True)
    gym_id     = Column(Integer, ForeignKey("gyms.id"), nullable=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(255), nullable=False, index=True)
    phone      = Column(String(30), nullable=True)
    status     = Column(String(30), nullable=False, default="new")
    # status values: "new" | "contacted" | "qualified" | "converted" | "lost"
    source     = Column(String(50), nullable=False, default="")
    # source values: "organic" | "referral" | "paid_ad" | "event" | "direct"
    notes      = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    gym = relationship("Gym", back_populates="leads")
