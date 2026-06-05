"""
Module: services.blockchain_service
Description: SHA-256 certificate generation and public verification.
             No external API dependencies — pure stdlib hashlib.
"""
import hashlib

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.blockchain import Certificate
from app.models.analysis import Analysis


def _build_payload(analysis: Analysis) -> str:
    """
    Construct the canonical string to hash.
    Format: "{analysis_id}:{user_id}:{global_score:.4f}:{completed_at_iso}"
    completed_at is used (not created_at) because it is set only when
    status='completed', making the hash stable once the analysis is done.
    """
    score = analysis.global_score if analysis.global_score is not None else 0.0
    ts    = analysis.completed_at.isoformat() if analysis.completed_at else ""
    return f"{analysis.id}:{analysis.user_id}:{score:.4f}:{ts}"


def get_or_create_certificate(db: Session, analysis_id: int) -> Certificate:
    """
    Generate (or retrieve existing) SHA-256 certificate for a completed analysis.
    Raises HTTPException 404 if analysis not found.
    Raises HTTPException 422 if analysis is not completed.
    Idempotent: returns existing certificate if already generated.
    """
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Análisis no encontrado.",
        )
    if analysis.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo se pueden certificar análisis con status 'completed'.",
        )

    # Idempotent: return existing certificate if already generated
    existing = db.query(Certificate).filter(
        Certificate.analysis_id == analysis_id
    ).first()
    if existing:
        return existing

    payload = _build_payload(analysis)
    digest  = hashlib.sha256(payload.encode("utf-8")).hexdigest()

    cert = Certificate(analysis_id=analysis_id, hash=digest)
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return cert


def verify_certificate(db: Session, hash_value: str) -> dict:
    """
    Public verification: find certificate by hash, increment verified_count,
    and return certificate data + recomputed hash match status.
    """
    cert = db.query(Certificate).filter(Certificate.hash == hash_value).first()
    if not cert:
        return {
            "valid": False,
            "certificate": None,
            "message": "Certificado no encontrado.",
        }

    # Recompute hash to confirm integrity
    payload    = _build_payload(cert.analysis)
    recomputed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    is_valid   = recomputed == hash_value

    if is_valid:
        cert.verified_count += 1
        db.commit()
        db.refresh(cert)
        message = "Certificado válido y verificado correctamente."
    else:
        message = "El certificado existe pero el hash no coincide — posible alteración de datos."

    return {"valid": is_valid, "certificate": cert, "message": message}
