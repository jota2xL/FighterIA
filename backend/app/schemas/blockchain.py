"""
Module: schemas.blockchain
Description: Pydantic v2 schemas for Certificate endpoints
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class CertificateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id:             int
    analysis_id:    int
    hash:           str
    issued_at:      datetime
    verified_count: int


class CertificateVerifyResponse(BaseModel):
    valid:       bool
    certificate: Optional[CertificateOut] = None
    message:     str
