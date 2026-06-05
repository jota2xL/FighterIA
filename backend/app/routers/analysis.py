"""
Module: routers.analysis
Description: Video upload, analysis processing, history, comparison and file download endpoints.

IMPORTANT — route ordering:
  /analysis/me and /analysis/compare MUST be declared before /analysis/{analysis_id}
  so FastAPI does not treat 'me' or 'compare' as an integer path parameter.
"""
import pathlib
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.analysis import Analysis, AnalysisComment
from app.schemas.analysis import (
    AnalysisDetailResponse,
    AnalysisListResponse,
    CommentCreate,
    CompareResponse,
)
from app.services import analysis_service, auth_service

router = APIRouter(prefix="/analysis", tags=["analysis"])

_ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi"}
_MAX_SIZE_MB = 200


@router.post("", response_model=AnalysisDetailResponse, status_code=201)
async def create_analysis(
    technique_id: int         = Form(...),
    video: UploadFile         = File(...),
    db: Session               = Depends(get_db),
    current_user              = Depends(auth_service.get_current_user),
):
    """
    Upload a video and run the full MediaPipe analysis pipeline synchronously.
    Client must set Axios timeout >= 300 000 ms before calling this endpoint.
    """
    ext = pathlib.Path(video.filename or "video.mp4").suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Formato no soportado: '{ext}'. Usa MP4, MOV o AVI.")

    content = await video.read()
    if len(content) > _MAX_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"El vídeo supera los {_MAX_SIZE_MB} MB permitidos.")

    return analysis_service.run_analysis(
        db=db,
        user=current_user,
        technique_id=technique_id,
        video_bytes=content,
        video_extension=ext,
    )


# ── /analysis/me must come before /analysis/{analysis_id} ──────────────────

@router.get("/me", response_model=AnalysisListResponse)
def list_my_analyses(
    page: int                   = Query(1, ge=1),
    limit: int                  = Query(20, ge=1, le=50),
    discipline_id: Optional[int] = Query(None),
    technique_id: Optional[int]  = Query(None),
    db: Session                 = Depends(get_db),
    current_user                = Depends(auth_service.get_current_user),
):
    """Return the authenticated user's paginated analysis history."""
    return analysis_service.get_user_analyses(
        db, current_user.id, page, limit, discipline_id, technique_id
    )


@router.get("/compare", response_model=CompareResponse)
def compare_analyses(
    id1: int       = Query(...),
    id2: int       = Query(...),
    db: Session    = Depends(get_db),
    current_user   = Depends(auth_service.get_current_user),
):
    """
    Side-by-side comparison of two analyses.
    Both must belong to the current user and reference the same technique.
    """
    return analysis_service.compare(db, current_user.id, id1, id2)


# ── Parameterised routes ────────────────────────────────────────────────────

@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    analysis_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Return the full detail of a single analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado.")
    if analysis.user_id != current_user.id:
        raise HTTPException(403, "No tienes acceso a este análisis.")
    return analysis_service._build_detail_response(analysis)


@router.get("/{analysis_id}/download/overlay")
def download_overlay(
    analysis_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_video_stream_user),
):
    """
    Stream the overlay MP4 video.
    Accepts JWT via ?token= query param so <video> elements can load it
    without requiring custom request headers.
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id,
    ).first()
    if not analysis or not analysis.video_overlay_path:
        raise HTTPException(404, "Vídeo con overlay no disponible.")
    path = pathlib.Path(analysis.video_overlay_path)
    if not path.exists():
        raise HTTPException(404, "Archivo de vídeo no encontrado en el servidor.")
    return FileResponse(
        str(path),
        media_type="video/mp4",
        filename=f"fighterai_overlay_{analysis_id}.mp4",
    )


@router.get("/{analysis_id}/download/original")
def download_original(
    analysis_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_video_stream_user),
):
    """
    Stream the original uploaded video.
    Accepts JWT via ?token= query param (same reason as download/overlay).
    """
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id,
    ).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado.")
    path = pathlib.Path(analysis.video_original_path)
    if not path.exists():
        raise HTTPException(404, "Archivo de vídeo original no encontrado.")
    ext = path.suffix.lower()
    _media_types = {".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo"}
    return FileResponse(
        str(path),
        media_type=_media_types.get(ext, "video/mp4"),
        filename=f"fighterai_original_{analysis_id}{ext}",
    )


@router.get("/{analysis_id}/comments")
def get_comments(
    analysis_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """Return all instructor comments on an analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado.")
    if analysis.user_id != current_user.id:
        raise HTTPException(403, "No tienes acceso a este análisis.")
    return [
        {
            "id": c.id,
            "content": c.content,
            "author_username": c.author.username,
            "author_avatar_url": c.author.avatar_url,
            "created_at": c.created_at,
        }
        for c in analysis.comments
    ]
