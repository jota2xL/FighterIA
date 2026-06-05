"""
Module: routers.instructor
Description: Instructor panel endpoints — group management, student progress and comments.
             All group-creation and view endpoints require account_type='instructor'.
             Students join groups via POST /instructor/groups/join (any authenticated user).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.instructor import (
    GroupCreate,
    GroupResponse,
    GroupDetailResponse,
    JoinGroupRequest,
)
from app.schemas.analysis import AnalysisListResponse, CommentCreate, CommentResponse
from app.schemas.dashboard import DashboardResponse
from app.services import auth_service, instructor_service

router = APIRouter(prefix="/instructor", tags=["instructor"])


@router.post("/groups", response_model=GroupResponse, status_code=201)
def create_group(
    payload: GroupCreate,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.require_instructor),
):
    """Create a new student group with a unique invite code."""
    return instructor_service.create_group(db, current_user, payload)


@router.get("/groups", response_model=List[GroupResponse])
def list_groups(
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.require_instructor),
):
    """Return all groups owned by the current instructor."""
    return instructor_service.get_groups(db, current_user.id)


@router.get("/groups/{group_id}", response_model=GroupDetailResponse)
def get_group(
    group_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.require_instructor),
):
    """Return group detail including member list with individual statistics."""
    return instructor_service.get_group_detail(db, group_id, current_user.id)


@router.post("/groups/join")
def join_group(
    payload: JoinGroupRequest,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.get_current_user),
):
    """
    Join a group using an invite code.
    Any authenticated user (alumno) can call this endpoint.
    Instructors cannot join groups as students.
    """
    return instructor_service.join_group(db, current_user, payload.invite_code)


@router.get("/students/{student_id}/analyses", response_model=AnalysisListResponse)
def get_student_analyses(
    student_id: int,
    page: int       = Query(1, ge=1),
    limit: int      = Query(20, ge=1, le=50),
    db: Session     = Depends(get_db),
    current_user    = Depends(auth_service.require_instructor),
):
    """Return the paginated analysis history of a student in one of the instructor's groups."""
    return instructor_service.get_student_analyses(db, current_user.id, student_id, page, limit)


@router.get("/students/{student_id}/stats", response_model=DashboardResponse)
def get_student_stats(
    student_id: int,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.require_instructor),
):
    """Return the full dashboard summary of a student in one of the instructor's groups."""
    return instructor_service.get_student_stats(db, current_user.id, student_id)


@router.post("/analyses/{analysis_id}/comment", status_code=201)
def add_comment(
    analysis_id: int,
    payload: CommentCreate,
    db: Session  = Depends(get_db),
    current_user = Depends(auth_service.require_instructor),
):
    """Leave a text comment on a student's analysis."""
    return instructor_service.add_comment(db, current_user, analysis_id, payload.content)
