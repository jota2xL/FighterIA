"""
Module: routers.blockchain
Description: Blockchain certificate endpoints — generate (auth required) and verify (public).
             Prefix: /blockchain | Tags: ["Blockchain"]
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.blockchain import CertificateOut, CertificateVerifyResponse
from app.services import blockchain_service
from app.services import auth_service
from app.models.analysis import Analysis

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


@router.post(
    "/certificates/generate/{analysis_id}",
    response_model=CertificateOut,
)
def generate_certificate(
    analysis_id:  int,
    db:           Session = Depends(get_db),
    current_user          = Depends(auth_service.get_current_user),
):
    """
    Generate a SHA-256 certificate for a completed analysis owned by the current user.
    - Returns HTTP 200 with the existing certificate if one was already issued (idempotent).
    - Returns HTTP 201 on first generation.
    - Raises HTTP 403 if the analysis does not belong to the current user.
    - Raises HTTP 422 if the analysis is not yet completed.
    - Raises HTTP 404 if the analysis does not exist.
    """
    # Ownership check — load analysis directly to verify user before delegating
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado.",
        )
    if analysis.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para certificar este análisis.",
        )

    # Delegate to service (handles completed check + idempotency)
    cert = blockchain_service.get_or_create_certificate(db, analysis_id)
    return cert


@router.get(
    "/certificates/{hash_value}",
    response_model=CertificateVerifyResponse,
)
def verify_certificate(
    hash_value: str,
    db:         Session = Depends(get_db),
):
    """
    Public endpoint — verify a certificate by its SHA-256 hash.
    No authentication required.
    Increments verified_count on successful validation.
    Always returns HTTP 200:
    - {"valid": true, "certificate": {...}, "message": "..."} if hash matches
    - {"valid": false, "certificate": null, "message": "..."} if not found
    - {"valid": false, "certificate": {...}, "message": "..."} if hash tampered
    """
    result = blockchain_service.verify_certificate(db, hash_value)
    return CertificateVerifyResponse(
        valid=result["valid"],
        certificate=result["certificate"],
        message=result["message"],
    )
