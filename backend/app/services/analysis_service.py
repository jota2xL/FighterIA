"""
Module: services.analysis_service
Description: Main orchestrator for the video analysis pipeline.
             Coordinates video storage, MediaPipe processing, scoring,
             feedback generation, gamification and persistence.
"""
from __future__ import annotations

import pathlib
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisJointResult, AnalysisFeedback
from app.models.discipline import Technique
from app.models.biomechanical import BiomechanicalReference
from app.models.user import User
from app.services.mediapipe_service import PoseAnalyzer
from app.services.scoring_service import calculate_scores
from app.services.feedback_service import generate_feedback
from app.services.gamification_service import (
    calculate_xp_reward,
    award_xp_and_update_belt,
    update_streak,
    check_and_award_badges,
)
from app.services.video_service import validate_duration
from app.utils.storage import get_original_video_path, get_overlay_video_path
from app.schemas.analysis import (
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisListItem,
    CompareResponse,
    JointResultSchema,
    FeedbackItemSchema,
    TechniqueMinimal,
    NewlyEarnedBadge,
)
from app.config import settings


# Base URL used to build download links in responses
_BASE_URL = "http://localhost:8000"


def run_analysis(
    db: Session,
    user: User,
    technique_id: int,
    video_bytes: bytes,
    video_extension: str,
) -> AnalysisDetailResponse:
    """
    Execute the full analysis pipeline synchronously.
    Steps:
      1  Validate technique exists
      2  Create Analysis record (status=pending)
      3  Save original video bytes to filesystem
      4  Validate video duration
      5  Load biomechanical references
      6  Run MediaPipe — detect pose and generate overlay
      7  Build joint results from measured vs reference angles
      8  Calculate scores
      9  Generate feedback
      10 Calculate XP reward
      11 Persist joint results and feedback
      12 Update analysis record (status=completed, scores)
      13 Gamification: XP, belt, streak, badges
      14 Commit and return AnalysisDetailResponse
    """
    # ── 1. Validate technique ────────────────────────────────────────────
    technique = db.query(Technique).filter(Technique.id == technique_id).first()
    if not technique:
        raise HTTPException(404, f"Técnica con id={technique_id} no encontrada.")

    # ── 2. Create pending Analysis record ────────────────────────────────
    analysis = Analysis(
        user_id=user.id,
        technique_id=technique_id,
        video_original_path="",  # updated after save
        status="pending",
    )
    db.add(analysis)
    db.flush()  # populate analysis.id

    # ── 3. Save original video ───────────────────────────────────────────
    original_path = get_original_video_path(user.id, analysis.id, video_extension)
    original_path.write_bytes(video_bytes)
    analysis.video_original_path = str(original_path)
    analysis.status = "processing"
    db.flush()

    # ── 4. Validate duration ─────────────────────────────────────────────
    try:
        validate_duration(original_path)
    except ValueError as exc:
        _fail_analysis(db, analysis, str(exc))
        raise HTTPException(400, str(exc))

    # ── 5. Load biomechanical references ─────────────────────────────────
    bio_refs_orm = (
        db.query(BiomechanicalReference)
        .filter(BiomechanicalReference.technique_id == technique_id)
        .all()
    )
    bio_refs: dict[str, dict] = {
        ref.joint_name: {
            "min_angle":    ref.min_angle,
            "max_angle":    ref.max_angle,
            "optimal_angle": ref.optimal_angle,
            "weight":       ref.weight,
        }
        for ref in bio_refs_orm
    }

    # ── 6. MediaPipe processing ──────────────────────────────────────────
    overlay_path = get_overlay_video_path(user.id, analysis.id)
    analyzer = PoseAnalyzer()
    try:
        video_result = analyzer.analyze_video(
            input_path=original_path,
            output_path=overlay_path,
            biomechanical_refs=bio_refs,
        )
    except Exception as exc:
        _fail_analysis(db, analysis, f"Error de procesamiento MediaPipe: {exc}")
        raise HTTPException(500, f"Error al procesar el vídeo: {exc}")
    finally:
        analyzer.close()

    if not video_result.pose_detected:
        msg = (
            "No se detectó ninguna persona en el vídeo. "
            "Asegúrate de que el cuerpo completo sea visible y la iluminación sea suficiente."
        )
        _fail_analysis(db, analysis, msg)
        raise HTTPException(500, msg)

    # ── 7. Build joint results data ──────────────────────────────────────
    joint_results_data: list[dict] = []
    for joint_name, ref in bio_refs.items():
        if joint_name not in video_result.joint_angles:
            continue
        measured = video_result.joint_angles[joint_name]
        is_correct = ref["min_angle"] <= measured <= ref["max_angle"]
        joint_results_data.append(
            {
                "joint_name":    joint_name,
                "measured_angle": measured,
                "ref_min":       ref["min_angle"],
                "ref_max":       ref["max_angle"],
                "optimal_angle": ref["optimal_angle"],
                "is_correct":    is_correct,
                "deviation":     measured - ref["optimal_angle"],
                "weight":        ref["weight"],
            }
        )

    # ── 8. Calculate scores ──────────────────────────────────────────────
    scores = calculate_scores(
        joint_results=joint_results_data,
        speed_proxy=video_result.speed_proxy,
        frame_count=video_result.frame_count,
    )

    # ── 9. Generate feedback ─────────────────────────────────────────────
    feedback_items = generate_feedback(joint_results_data)

    # ── 10. XP reward ────────────────────────────────────────────────────
    xp_reward = calculate_xp_reward(scores["global_score"], technique.xp_multiplier)

    # ── 11. Persist joint results ────────────────────────────────────────
    for jr in joint_results_data:
        db.add(
            AnalysisJointResult(
                analysis_id=analysis.id,
                joint_name=jr["joint_name"],
                measured_angle=jr["measured_angle"],
                reference_min=jr["ref_min"],
                reference_max=jr["ref_max"],
                optimal_angle=jr["optimal_angle"],
                is_correct=jr["is_correct"],
                deviation=jr["deviation"],
            )
        )

    for fb in feedback_items:
        db.add(
            AnalysisFeedback(
                analysis_id=analysis.id,
                correction_title=fb["correction_title"],
                correction_text=fb["correction_text"],
                biomechanical_explanation=fb.get("biomechanical_explanation"),
                exercise_suggestion=fb.get("exercise_suggestion"),
                priority_order=fb["priority_order"],
                impact_score=fb["impact_score"],
            )
        )

    # ── 12. Update analysis record ───────────────────────────────────────
    analysis.video_overlay_path = str(overlay_path)
    analysis.status = "completed"
    analysis.global_score = scores["global_score"]
    analysis.power_score = scores["power_score"]
    analysis.balance_score = scores["balance_score"]
    analysis.alignment_score = scores["alignment_score"]
    analysis.speed_score = scores["speed_score"]
    analysis.xp_awarded = xp_reward
    analysis.completed_at = datetime.now(timezone.utc)
    db.flush()

    # ── 13. Gamification ─────────────────────────────────────────────────
    gamification_result = award_xp_and_update_belt(user, xp_reward, db)
    update_streak(user, db)
    newly_earned_badges = check_and_award_badges(user, db)

    # ── 14. Commit ───────────────────────────────────────────────────────
    db.commit()
    db.refresh(analysis)

    return _build_detail_response(
        analysis,
        belt_upgraded=gamification_result["belt_upgraded"],
        new_belt=gamification_result["new_belt"] if gamification_result["belt_upgraded"] else None,
        newly_earned_badges=newly_earned_badges,
    )


def get_user_analyses(
    db: Session,
    user_id: int,
    page: int,
    limit: int,
    discipline_id: Optional[int] = None,
    technique_id: Optional[int] = None,
) -> AnalysisListResponse:
    """Return paginated analysis history for a user, optionally filtered."""
    query = db.query(Analysis).filter(Analysis.user_id == user_id)

    if discipline_id:
        query = query.join(Technique, Analysis.technique_id == Technique.id).filter(
            Technique.discipline_id == discipline_id
        )
    if technique_id:
        query = query.filter(Analysis.technique_id == technique_id)

    total = query.count()
    analyses = (
        query.order_by(Analysis.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    items = [_to_list_item(a) for a in analyses]
    pages = max(1, (total + limit - 1) // limit)

    return AnalysisListResponse(items=items, total=total, page=page, limit=limit, pages=pages)


def compare(db: Session, user_id: int, id1: int, id2: int) -> CompareResponse:
    """Compare two analyses from the same user and same technique."""
    a1 = db.query(Analysis).filter(Analysis.id == id1, Analysis.user_id == user_id).first()
    a2 = db.query(Analysis).filter(Analysis.id == id2, Analysis.user_id == user_id).first()

    if not a1 or not a2:
        raise HTTPException(404, "Uno o ambos análisis no encontrados o no te pertenecen.")
    if a1.technique_id != a2.technique_id:
        raise HTTPException(400, "Solo puedes comparar análisis de la misma técnica.")

    score_diff = round((a1.global_score or 0.0) - (a2.global_score or 0.0), 1)

    a1_joints = {jr.joint_name: jr.is_correct for jr in a1.joint_results}
    a2_joints = {jr.joint_name: jr.is_correct for jr in a2.joint_results}
    improved  = [j for j in a1_joints if a1_joints[j] and not a2_joints.get(j, True)]
    regressed = [j for j in a1_joints if not a1_joints[j] and a2_joints.get(j, False)]

    return CompareResponse(
        analysis_1=_build_detail_response(a1),
        analysis_2=_build_detail_response(a2),
        score_difference=score_diff,
        improved_joints=improved,
        regressed_joints=regressed,
        improved=score_diff > 0,
    )


# ── Helpers ───────────────────────────────────────────────────────────────

def _fail_analysis(db: Session, analysis: Analysis, message: str) -> None:
    """Mark an analysis as failed and commit."""
    analysis.status = "failed"
    analysis.error_message = message
    try:
        db.commit()
    except Exception:
        db.rollback()


def _build_detail_response(
    analysis: Analysis,
    belt_upgraded: bool = False,
    new_belt: Optional[str] = None,
    newly_earned_badges: list = None,
) -> AnalysisDetailResponse:
    """Assemble an AnalysisDetailResponse from an Analysis ORM object."""
    technique_minimal = None
    if analysis.technique:
        technique_minimal = TechniqueMinimal(
            id=analysis.technique.id,
            name=analysis.technique.name,
            display_name=analysis.technique.display_name,
            discipline_name=analysis.technique.discipline.display_name,
            difficulty=analysis.technique.difficulty,
        )

    overlay_url = (
        f"{_BASE_URL}/analysis/{analysis.id}/download/overlay"
        if analysis.video_overlay_path
        else None
    )
    original_url = f"{_BASE_URL}/analysis/{analysis.id}/download/original"

    return AnalysisDetailResponse(
        id=analysis.id,
        status=analysis.status,
        technique=technique_minimal,
        global_score=analysis.global_score,
        power_score=analysis.power_score,
        balance_score=analysis.balance_score,
        alignment_score=analysis.alignment_score,
        speed_score=analysis.speed_score,
        xp_awarded=analysis.xp_awarded,
        belt_upgraded=belt_upgraded,
        new_belt=new_belt,
        newly_earned_badges=[NewlyEarnedBadge(**b) for b in (newly_earned_badges or [])],
        joint_results=[JointResultSchema.model_validate(jr) for jr in (analysis.joint_results or [])],
        feedback=[FeedbackItemSchema.model_validate(fb) for fb in (analysis.feedback or [])],
        video_overlay_url=overlay_url,
        video_original_url=original_url,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message,
    )


def _to_list_item(analysis: Analysis) -> AnalysisListItem:
    """Convert an Analysis ORM object to a list-view item schema."""
    overlay_url = (
        f"{_BASE_URL}/analysis/{analysis.id}/download/overlay"
        if analysis.video_overlay_path
        else None
    )
    return AnalysisListItem(
        id=analysis.id,
        technique_display_name=analysis.technique.display_name if analysis.technique else "—",
        discipline_name=(
            analysis.technique.discipline.display_name
            if analysis.technique and analysis.technique.discipline
            else "—"
        ),
        global_score=analysis.global_score,
        status=analysis.status,
        video_overlay_url=overlay_url,
        created_at=analysis.created_at,
    )
