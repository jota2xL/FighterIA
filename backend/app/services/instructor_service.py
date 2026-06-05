"""
Module: services.instructor_service
Description: Group management, student progress views and instructor comment operations
"""
from __future__ import annotations

import secrets
import string
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisComment
from app.models.instructor import GroupMember, InstructorGroup
from app.models.user import User
from app.schemas.instructor import (
    GroupCreate,
    GroupDetailResponse,
    GroupMemberSummary,
    GroupResponse,
)


def _generate_invite_code(length: int = 8) -> str:
    """Generate a random alphanumeric invite code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _unique_invite_code(db: Session) -> str:
    """Generate an invite code that is not already in use."""
    for _ in range(10):
        code = _generate_invite_code()
        if not db.query(InstructorGroup).filter(InstructorGroup.invite_code == code).first():
            return code
    raise RuntimeError("Could not generate a unique invite code after 10 attempts.")


# ── Group management ──────────────────────────────────────────────────────

def create_group(db: Session, instructor: User, payload: GroupCreate) -> GroupResponse:
    if instructor.account_type != "instructor":
        raise HTTPException(403, "Solo los instructores pueden crear grupos.")
    group = InstructorGroup(
        instructor_id=instructor.id,
        name=payload.name,
        description=payload.description,
        invite_code=_unique_invite_code(db),
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return GroupResponse(
        id=group.id,
        name=group.name,
        description=group.description,
        invite_code=group.invite_code,
        member_count=0,
        is_active=group.is_active,
        created_at=group.created_at,
    )


def get_groups(db: Session, instructor_id: int) -> list[GroupResponse]:
    groups = (
        db.query(InstructorGroup)
        .filter(InstructorGroup.instructor_id == instructor_id)
        .order_by(InstructorGroup.created_at.desc())
        .all()
    )
    return [
        GroupResponse(
            id=g.id,
            name=g.name,
            description=g.description,
            invite_code=g.invite_code,
            member_count=len(g.members),
            is_active=g.is_active,
            created_at=g.created_at,
        )
        for g in groups
    ]


def get_group_detail(db: Session, group_id: int, instructor_id: int) -> GroupDetailResponse:
    group = db.query(InstructorGroup).filter(
        InstructorGroup.id == group_id,
        InstructorGroup.instructor_id == instructor_id,
    ).first()
    if not group:
        raise HTTPException(404, "Grupo no encontrado o no te pertenece.")

    members = []
    for gm in group.members:
        student = gm.student
        stats = db.query(
            func.count(Analysis.id).label("total"),
            func.avg(Analysis.global_score).label("avg"),
        ).filter(
            Analysis.user_id == student.id,
            Analysis.status == "completed",
        ).first()

        members.append(
            GroupMemberSummary(
                student_id=student.id,
                username=student.username,
                full_name=student.full_name,
                belt_level=student.belt_level,
                xp=student.xp or 0,
                total_analyses=stats.total or 0,
                last_activity_date=student.last_activity_date,
                average_score=round(stats.avg, 1) if stats.avg else None,
                joined_at=gm.joined_at,
            )
        )

    return GroupDetailResponse(
        id=group.id,
        name=group.name,
        invite_code=group.invite_code,
        members=members,
    )


def join_group(db: Session, student: User, invite_code: str) -> dict:
    """Add a student to a group via invite code."""
    if student.account_type == "instructor":
        raise HTTPException(403, "Los instructores no pueden unirse a grupos como alumnos.")

    group = db.query(InstructorGroup).filter(
        InstructorGroup.invite_code == invite_code,
        InstructorGroup.is_active == True,
    ).first()
    if not group:
        raise HTTPException(404, "Código de invitación inválido o grupo inactivo.")

    existing = db.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.student_id == student.id,
    ).first()
    if existing:
        raise HTTPException(409, "Ya eres miembro de este grupo.")

    db.add(GroupMember(group_id=group.id, student_id=student.id))
    db.commit()
    return {"message": f"Te has unido al grupo '{group.name}' correctamente.", "group_name": group.name}


# ── Student views ─────────────────────────────────────────────────────────

def _assert_instructor_has_student(db: Session, instructor_id: int, student_id: int) -> None:
    """Raise 403 if the instructor does not have this student in any of their groups."""
    exists = (
        db.query(GroupMember)
        .join(InstructorGroup, GroupMember.group_id == InstructorGroup.id)
        .filter(
            InstructorGroup.instructor_id == instructor_id,
            GroupMember.student_id == student_id,
        )
        .first()
    )
    if not exists:
        raise HTTPException(403, "Este alumno no pertenece a ninguno de tus grupos.")


def get_student_analyses(
    db: Session,
    instructor_id: int,
    student_id: int,
    page: int,
    limit: int,
) -> dict:
    _assert_instructor_has_student(db, instructor_id, student_id)
    from app.services.analysis_service import get_user_analyses
    return get_user_analyses(db, student_id, page, limit)


def get_student_stats(db: Session, instructor_id: int, student_id: int) -> dict:
    _assert_instructor_has_student(db, instructor_id, student_id)
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(404, "Alumno no encontrado.")
    from app.services.dashboard_service import get_dashboard
    return get_dashboard(db, student)


# ── Comments ──────────────────────────────────────────────────────────────

def add_comment(
    db: Session,
    instructor: User,
    analysis_id: int,
    content: str,
) -> dict:
    """Add an instructor comment to a student's analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado.")

    _assert_instructor_has_student(db, instructor.id, analysis.user_id)

    comment = AnalysisComment(
        analysis_id=analysis_id,
        author_id=instructor.id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "author_username": instructor.username,
        "author_avatar_url": instructor.avatar_url,
        "created_at": comment.created_at,
    }
