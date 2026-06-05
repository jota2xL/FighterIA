"""
Module: models.blockchain
Description: Certificate model — SHA-256 proof of completed analysis
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id             = Column(Integer, primary_key=True, index=True)
    analysis_id    = Column(Integer, ForeignKey("analyses.id"),
                            nullable=False, unique=True, index=True)
    hash           = Column(String(64), nullable=False, unique=True, index=True)
    # 64 hex chars = SHA-256 output
    issued_at      = Column(DateTime(timezone=True),
                            server_default=func.now(), nullable=False)
    verified_count = Column(Integer, default=0, nullable=False)

    analysis = relationship("Analysis", lazy="select")
