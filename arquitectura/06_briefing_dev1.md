# Arquitectura FighterIA — Entregable 6: Briefing Dev1 (Backend)

> **Autor:** Agente Arquitecto de Software Senior
> **Destinatario:** Agente Dev1 — Desarrollador Backend Senior
> **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Tu misión

Implementar el backend completo de FighterIA. Tienes todo lo que necesitas en este documento y en los entregables del Arquitecto. No preguntes nada — toma las decisiones de implementación que necesites y documéntalas en tu reporte final.

---

## 2. Stack exacto

```
Python 3.11
FastAPI 0.111.0
uvicorn[standard] 0.29.0
SQLAlchemy 2.0.30
pydantic 2.7.1
pydantic-settings 2.2.1
python-dotenv 1.0.1
python-jose[cryptography] 3.3.0
passlib[bcrypt] 1.7.4
python-multipart 0.0.9
mediapipe 0.10.14
opencv-python-headless 4.9.0.80
numpy 1.26.4
pytest 8.2.0
httpx 0.27.0
faker 24.11.0
```

**Arranque:** `uvicorn app.main:app --reload --port 8000`

---

## 3. Schemas Pydantic — Implementación Completa

El Arquitecto define los schemas que Dev1 debe implementar exactamente.

### `app/schemas/auth.py`
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .user import UserResponse


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)
    account_type: str = Field(..., pattern=r'^(alumno|instructor)$')


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
```

### `app/schemas/user.py`
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import json


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    account_type: str
    bio: Optional[str] = None
    gym: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    experience_years: int = 0
    disciplines: List[str] = []
    avatar_url: Optional[str] = None
    xp: int = 0
    belt_level: str = "blanco"
    current_streak: int = 0
    max_streak: int = 0
    streak_shields: int = 0
    is_active: bool = True
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Convert JSON string disciplines to list
        if hasattr(obj, 'disciplines') and isinstance(obj.disciplines, str):
            try:
                obj.__dict__['disciplines'] = json.loads(obj.disciplines)
            except (json.JSONDecodeError, TypeError):
                obj.__dict__['disciplines'] = []
        return super().model_validate(obj, *args, **kwargs)


class PublicUserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    account_type: str
    bio: Optional[str] = None
    gym: Optional[str] = None
    belt_level: str
    xp: int
    current_streak: int
    avatar_url: Optional[str] = None
    total_analyses: int = 0
    best_score: Optional[float] = None
    average_score: Optional[float] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    gym: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    experience_years: Optional[int] = Field(None, ge=0, le=100)
    disciplines: Optional[str] = None  # JSON string from form
```

### `app/schemas/discipline.py`
```python
from pydantic import BaseModel
from typing import Optional


class DisciplineResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None

    model_config = {"from_attributes": True}


class TechniqueResponse(BaseModel):
    id: int
    discipline_id: int
    name: str
    display_name: str
    description: Optional[str] = None
    difficulty: str
    xp_multiplier: float

    model_config = {"from_attributes": True}
```

### `app/schemas/analysis.py`
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TechniqueMinimal(BaseModel):
    id: int
    name: str
    display_name: str
    discipline_name: str
    difficulty: str

    model_config = {"from_attributes": True}


class JointResultSchema(BaseModel):
    joint_name: str
    measured_angle: float
    reference_min: float
    reference_max: float
    optimal_angle: float
    is_correct: bool
    deviation: float

    model_config = {"from_attributes": True}


class FeedbackItemSchema(BaseModel):
    priority_order: int
    correction_title: str
    correction_text: str
    biomechanical_explanation: Optional[str] = None
    exercise_suggestion: Optional[str] = None
    impact_score: float

    model_config = {"from_attributes": True}


class NewlyEarnedBadge(BaseModel):
    badge_id: int
    display_name: str
    xp_reward: int


class AnalysisDetailResponse(BaseModel):
    id: int
    status: str
    technique: Optional[TechniqueMinimal] = None
    global_score: Optional[float] = None
    power_score: Optional[float] = None
    balance_score: Optional[float] = None
    alignment_score: Optional[float] = None
    speed_score: Optional[float] = None
    xp_awarded: int = 0
    belt_upgraded: bool = False
    new_belt: Optional[str] = None
    newly_earned_badges: List[NewlyEarnedBadge] = []
    joint_results: List[JointResultSchema] = []
    feedback: List[FeedbackItemSchema] = []
    video_overlay_url: Optional[str] = None
    video_original_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class AnalysisListItem(BaseModel):
    id: int
    technique_display_name: str
    discipline_name: str
    global_score: Optional[float] = None
    status: str
    video_overlay_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    items: List[AnalysisListItem]
    total: int
    page: int
    limit: int
    pages: int


class CompareResponse(BaseModel):
    analysis_1: AnalysisDetailResponse
    analysis_2: AnalysisDetailResponse
    score_difference: float
    improved_joints: List[str]
    regressed_joints: List[str]
    improved: bool


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=5, max_length=2000)


class CommentResponse(BaseModel):
    id: int
    content: str
    author_username: str
    author_avatar_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
```

### `app/schemas/dashboard.py`
```python
from pydantic import BaseModel
from typing import Optional, List


class RecentBadge(BaseModel):
    badge_id: int
    display_name: str
    icon_name: str
    level: str
    earned_at: str


class RecentAnalysis(BaseModel):
    id: int
    technique_display_name: str
    discipline_name: str
    global_score: Optional[float]
    created_at: str


class DashboardResponse(BaseModel):
    total_analyses: int
    best_score: Optional[float]
    average_score: Optional[float]
    favorite_discipline: Optional[str]
    most_analyzed_technique: Optional[str]
    xp: int
    belt_level: str
    xp_for_next_belt: Optional[int]
    xp_next_belt_name: Optional[str]
    current_streak: int
    max_streak: int
    streak_shields: int
    recent_badges: List[RecentBadge]
    recent_analyses: List[RecentAnalysis]


class ProgressDataset(BaseModel):
    discipline: str
    discipline_id: int
    color: str
    data: List[Optional[float]]


class ProgressResponse(BaseModel):
    labels: List[str]
    datasets: List[ProgressDataset]


class HeatmapEntry(BaseModel):
    date: str
    count: int


class HeatmapResponse(BaseModel):
    data: List[HeatmapEntry]
```

### `app/schemas/gamification.py`
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BadgeResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    level: str
    icon_name: str
    xp_reward: int

    model_config = {"from_attributes": True}


class UserBadgeResponse(BaseModel):
    badge_id: int
    display_name: str
    icon_name: str
    level: str
    xp_reward: int
    earned_at: datetime

    model_config = {"from_attributes": True}


class RankingItem(BaseModel):
    rank: int
    user_id: int
    username: str
    full_name: str
    belt_level: str
    xp: int
    average_score: Optional[float] = None
    avatar_url: Optional[str] = None


class RankingResponse(BaseModel):
    items: List[RankingItem]
    my_rank: Optional[int]
    total_users: int


class ShieldResponse(BaseModel):
    message: str
    shields_remaining: int
    xp_remaining: Optional[int] = None
    streak_protected: Optional[bool] = None
```

### `app/schemas/instructor.py`
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class GroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    invite_code: str
    member_count: int
    is_active: bool
    created_at: datetime


class GroupMemberSummary(BaseModel):
    student_id: int
    username: str
    full_name: str
    belt_level: str
    xp: int
    total_analyses: int
    last_activity_date: Optional[date]
    average_score: Optional[float]
    joined_at: datetime


class GroupDetailResponse(BaseModel):
    id: int
    name: str
    invite_code: str
    members: List[GroupMemberSummary]


class JoinGroupRequest(BaseModel):
    invite_code: str = Field(..., min_length=4, max_length=20)
```

---

## 4. Routers — Implementación de los 7 Routers

### `app/routers/auth.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshRequest,
    ForgotPasswordRequest, TokenResponse, RefreshTokenResponse, MessageResponse
)
from app.schemas.user import UserResponse
from app.services import auth_service, user_service
from app.utils.security import create_access_token, create_refresh_token, decode_token
from jose import JWTError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if user_service.get_by_email(db, payload.email):
        raise HTTPException(409, "Este email ya está registrado")
    if user_service.get_by_username(db, payload.username):
        raise HTTPException(409, "Este nombre de usuario ya está en uso")
    user = user_service.create(db, payload)
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Email o contraseña incorrectos")
    access = create_access_token({"sub": str(user.id)})
    refresh = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access, refresh_token=refresh, user=UserResponse.model_validate(user))


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(401, "Token inválido")
        user = user_service.get_by_id(db, int(data["sub"]))
        if not user:
            raise HTTPException(401, "Usuario no encontrado")
    except JWTError:
        raise HTTPException(401, "Token de refresco inválido o expirado")
    access = create_access_token({"sub": str(user.id)})
    refresh_new = create_refresh_token({"sub": str(user.id)})
    return RefreshTokenResponse(access_token=access, refresh_token=refresh_new)


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest):
    # Mock implementation — does not send real email
    return MessageResponse(message="Si este email está registrado, recibirás instrucciones en breve")


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(auth_service.get_current_user)):
    return current_user
```

### `app/routers/analysis.py`
```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import pathlib
from app.database import get_db
from app.services import auth_service, analysis_service
from app.schemas.analysis import (
    AnalysisDetailResponse, AnalysisListResponse, CompareResponse,
    CommentCreate, CommentResponse
)
from app.models.analysis import Analysis, AnalysisComment

router = APIRouter(prefix="/analysis", tags=["analysis"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi"}
MAX_VIDEO_SIZE_MB = 200


@router.post("", response_model=AnalysisDetailResponse, status_code=201)
async def create_analysis(
    technique_id: int = Form(...),
    video: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    ext = pathlib.Path(video.filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(400, f"Formato no soportado. Usa MP4, MOV o AVI")

    content = await video.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_VIDEO_SIZE_MB:
        raise HTTPException(400, f"El vídeo supera los {MAX_VIDEO_SIZE_MB}MB")

    return analysis_service.run_analysis(
        db=db,
        user=current_user,
        technique_id=technique_id,
        video_bytes=content,
        video_extension=ext
    )


@router.get("/me", response_model=AnalysisListResponse)
def list_my_analyses(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    discipline_id: Optional[int] = Query(None),
    technique_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    return analysis_service.get_user_analyses(db, current_user.id, page, limit, discipline_id, technique_id)


@router.get("/compare", response_model=CompareResponse)
def compare_analyses(
    id1: int = Query(...),
    id2: int = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    return analysis_service.compare(db, current_user.id, id1, id2)


@router.get("/{analysis_id}", response_model=AnalysisDetailResponse)
def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(403, "No tienes acceso a este análisis")
    return analysis_service.build_detail_response(analysis)


@router.get("/{analysis_id}/download/overlay")
def download_overlay(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    if not analysis or not analysis.video_overlay_path:
        raise HTTPException(404, "Vídeo con overlay no disponible")
    path = pathlib.Path(analysis.video_overlay_path)
    if not path.exists():
        raise HTTPException(404, "Archivo de vídeo no encontrado en el servidor")
    return FileResponse(str(path), media_type="video/mp4", filename=f"fighterai_analysis_{analysis_id}_overlay.mp4")


@router.get("/{analysis_id}/download/original")
def download_original(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado")
    path = pathlib.Path(analysis.video_original_path)
    if not path.exists():
        raise HTTPException(404, "Archivo de vídeo original no encontrado")
    ext = path.suffix.lower()
    media_type = {"mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo"}.get(ext, "video/mp4")
    return FileResponse(str(path), media_type=media_type, filename=f"fighterai_original_{analysis_id}{ext}")


@router.get("/{analysis_id}/comments")
def get_comments(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user)
):
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(404, "Análisis no encontrado")
    if analysis.user_id != current_user.id:
        raise HTTPException(403, "No tienes acceso")
    comments = db.query(AnalysisComment).filter(AnalysisComment.analysis_id == analysis_id).all()
    return [
        {
            "id": c.id,
            "content": c.content,
            "author_username": c.author.username,
            "author_avatar_url": c.author.avatar_url,
            "created_at": c.created_at
        }
        for c in comments
    ]
```

---

## 5. Servicio de Orquestación — `app/services/analysis_service.py`

Este es el componente más crítico del backend. Orquesta el pipeline completo.

```python
"""
Module: services.analysis_service
Description: Orchestrates the full video analysis pipeline:
             validate → save → process with MediaPipe → score → feedback
             → gamification → persist results
"""
import pathlib
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.analysis import Analysis, AnalysisJointResult, AnalysisFeedback
from app.models.discipline import Technique
from app.models.biomechanical import BiomechanicalReference
from app.models.user import User
from app.services.mediapipe_service import PoseAnalyzer
from app.services.scoring_service import calculate_scores
from app.services.feedback_service import generate_feedback
from app.services.gamification_service import (
    calculate_xp_reward, award_xp_and_update_belt, update_streak, check_and_award_badges
)
from app.utils.storage import get_original_video_path, get_overlay_video_path
from app.schemas.analysis import (
    AnalysisDetailResponse, AnalysisListResponse, CompareResponse,
    AnalysisListItem, JointResultSchema, FeedbackItemSchema,
    TechniqueMinimal, NewlyEarnedBadge
)
from fastapi import HTTPException


def run_analysis(
    db: Session,
    user: User,
    technique_id: int,
    video_bytes: bytes,
    video_extension: str
) -> AnalysisDetailResponse:
    """
    Full analysis pipeline. Synchronous — caller blocks until complete.
    Returns AnalysisDetailResponse ready for the HTTP response.
    """
    # 1. Validate technique exists
    technique = db.query(Technique).filter(Technique.id == technique_id).first()
    if not technique:
        raise HTTPException(404, f"Técnica con id={technique_id} no encontrada")

    # 2. Create analysis record (status=pending)
    analysis = Analysis(
        user_id=user.id,
        technique_id=technique_id,
        video_original_path="",  # updated after save
        status="pending"
    )
    db.add(analysis)
    db.flush()  # get analysis.id

    # 3. Save original video to filesystem
    original_path = get_original_video_path(user.id, analysis.id, video_extension)
    original_path.write_bytes(video_bytes)
    analysis.video_original_path = str(original_path)
    analysis.status = "processing"
    db.flush()

    # 4. Load biomechanical references for this technique
    bio_refs_orm = db.query(BiomechanicalReference).filter(
        BiomechanicalReference.technique_id == technique_id
    ).all()

    bio_refs_dict = {
        ref.joint_name: {
            "min_angle": ref.min_angle,
            "max_angle": ref.max_angle,
            "optimal_angle": ref.optimal_angle,
            "weight": ref.weight
        }
        for ref in bio_refs_orm
    }

    # 5. Run MediaPipe analysis and generate overlay
    overlay_path = get_overlay_video_path(user.id, analysis.id)
    analyzer = PoseAnalyzer()
    try:
        video_result = analyzer.analyze_video(
            input_path=original_path,
            output_path=overlay_path,
            biomechanical_refs=bio_refs_dict
        )
    except Exception as e:
        analysis.status = "failed"
        analysis.error_message = f"Error de procesamiento MediaPipe: {str(e)}"
        db.commit()
        raise HTTPException(500, f"Error al procesar el vídeo: {str(e)}")
    finally:
        analyzer.close()

    if not video_result.pose_detected:
        analysis.status = "failed"
        analysis.error_message = "No se detectó ninguna persona en el vídeo. Asegúrate de que el cuerpo completo sea visible."
        db.commit()
        raise HTTPException(500, analysis.error_message)

    # 6. Build joint results from measured angles vs references
    joint_results_data = []
    for joint_name, ref in bio_refs_dict.items():
        if joint_name not in video_result.joint_angles:
            continue
        measured = video_result.joint_angles[joint_name]
        is_correct = ref["min_angle"] <= measured <= ref["max_angle"]
        deviation = measured - ref["optimal_angle"]
        joint_results_data.append({
            "joint_name": joint_name,
            "measured_angle": measured,
            "reference_min": ref["min_angle"],
            "reference_max": ref["max_angle"],
            "optimal_angle": ref["optimal_angle"],
            "is_correct": is_correct,
            "deviation": deviation,
            "weight": ref["weight"]
        })

    # 7. Calculate scores
    scores = calculate_scores(
        joint_results=joint_results_data,
        speed_proxy=video_result.speed_proxy,
        frame_count=video_result.frame_count
    )

    # 8. Generate feedback
    feedback_data = generate_feedback(joint_results_data)

    # 9. Validate video duration (post-processing check)
    if video_result.frame_count == 0:
        analysis.status = "failed"
        analysis.error_message = "No se pudo leer el vídeo. Verifica el formato."
        db.commit()
        raise HTTPException(500, analysis.error_message)

    # 10. Calculate XP reward
    xp_reward = calculate_xp_reward(scores["global_score"], technique.xp_multiplier)

    # 11. Persist joint results
    for jr_data in joint_results_data:
        jr = AnalysisJointResult(
            analysis_id=analysis.id,
            joint_name=jr_data["joint_name"],
            measured_angle=jr_data["measured_angle"],
            reference_min=jr_data["reference_min"],
            reference_max=jr_data["reference_max"],
            optimal_angle=jr_data["optimal_angle"],
            is_correct=jr_data["is_correct"],
            deviation=jr_data["deviation"]
        )
        db.add(jr)

    # 12. Persist feedback
    for fb_data in feedback_data:
        fb = AnalysisFeedback(
            analysis_id=analysis.id,
            correction_title=fb_data["correction_title"],
            correction_text=fb_data["correction_text"],
            biomechanical_explanation=fb_data.get("biomechanical_explanation"),
            exercise_suggestion=fb_data.get("exercise_suggestion"),
            priority_order=fb_data["priority_order"],
            impact_score=fb_data["impact_score"]
        )
        db.add(fb)

    # 13. Update analysis record
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

    # 14. Gamification: XP, belt, streak, badges
    gamification_result = award_xp_and_update_belt(user, xp_reward, db)
    update_streak(user, db)
    newly_earned_badges = check_and_award_badges(user, db)

    db.commit()
    db.refresh(analysis)

    # 15. Build response
    return build_detail_response(
        analysis,
        belt_upgraded=gamification_result["belt_upgraded"],
        new_belt=gamification_result["new_belt"] if gamification_result["belt_upgraded"] else None,
        newly_earned_badges=newly_earned_badges
    )


def build_detail_response(
    analysis: Analysis,
    belt_upgraded: bool = False,
    new_belt: str = None,
    newly_earned_badges: list = None
) -> AnalysisDetailResponse:
    """Build AnalysisDetailResponse from an Analysis ORM object."""
    technique_minimal = None
    if analysis.technique:
        technique_minimal = TechniqueMinimal(
            id=analysis.technique.id,
            name=analysis.technique.name,
            display_name=analysis.technique.display_name,
            discipline_name=analysis.technique.discipline.display_name,
            difficulty=analysis.technique.difficulty
        )

    base_url = "http://localhost:8000"
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
        joint_results=[JointResultSchema.model_validate(jr) for jr in analysis.joint_results],
        feedback=[FeedbackItemSchema.model_validate(fb) for fb in analysis.feedback],
        video_overlay_url=f"{base_url}/analysis/{analysis.id}/download/overlay" if analysis.video_overlay_path else None,
        video_original_url=f"{base_url}/analysis/{analysis.id}/download/original",
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        error_message=analysis.error_message
    )


def get_user_analyses(
    db: Session,
    user_id: int,
    page: int,
    limit: int,
    discipline_id: int = None,
    technique_id: int = None
) -> AnalysisListResponse:
    """Return paginated analysis history for a user."""
    from app.models.discipline import Technique
    query = db.query(Analysis).filter(Analysis.user_id == user_id)
    if discipline_id:
        query = query.join(Technique).filter(Technique.discipline_id == discipline_id)
    if technique_id:
        query = query.filter(Analysis.technique_id == technique_id)

    total = query.count()
    analyses = query.order_by(Analysis.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    items = []
    for a in analyses:
        items.append(AnalysisListItem(
            id=a.id,
            technique_display_name=a.technique.display_name if a.technique else "—",
            discipline_name=a.technique.discipline.display_name if a.technique else "—",
            global_score=a.global_score,
            status=a.status,
            video_overlay_url=f"http://localhost:8000/analysis/{a.id}/download/overlay" if a.video_overlay_path else None,
            created_at=a.created_at
        ))

    return AnalysisListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=(total + limit - 1) // limit
    )


def compare(db: Session, user_id: int, id1: int, id2: int) -> CompareResponse:
    """Compare two analyses from the same user and technique."""
    a1 = db.query(Analysis).filter(Analysis.id == id1, Analysis.user_id == user_id).first()
    a2 = db.query(Analysis).filter(Analysis.id == id2, Analysis.user_id == user_id).first()

    if not a1 or not a2:
        raise HTTPException(404, "Uno o ambos análisis no encontrados")
    if a1.technique_id != a2.technique_id:
        raise HTTPException(400, "Solo puedes comparar análisis de la misma técnica")

    diff = round((a1.global_score or 0) - (a2.global_score or 0), 1)

    # Find which joints improved or regressed
    a1_joints = {jr.joint_name: jr.is_correct for jr in a1.joint_results}
    a2_joints = {jr.joint_name: jr.is_correct for jr in a2.joint_results}
    improved = [j for j in a1_joints if a1_joints[j] and not a2_joints.get(j, True)]
    regressed = [j for j in a1_joints if not a1_joints[j] and a2_joints.get(j, False)]

    return CompareResponse(
        analysis_1=build_detail_response(a1),
        analysis_2=build_detail_response(a2),
        score_difference=diff,
        improved_joints=improved,
        regressed_joints=regressed,
        improved=diff > 0
    )
```

---

## 6. Servicio `auth_service.py` — Dependencia `get_current_user`

```python
"""
Module: services.auth_service
Description: Authentication helpers and get_current_user FastAPI dependency
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from app.database import get_db
from app.utils.security import verify_password, decode_token
from app.models.user import User

bearer_scheme = HTTPBearer()


def authenticate(db: Session, email: str, password: str):
    """Return user if credentials are valid, None otherwise."""
    user = db.query(User).filter(User.email == email, User.is_active == True).first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency — validates Bearer token and returns the current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        token = credentials.credentials
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise credentials_exception
    return user


def require_instructor(current_user: User = Depends(get_current_user)) -> User:
    """Dependency — raises 403 if the current user is not an instructor."""
    if current_user.account_type != "instructor":
        raise HTTPException(403, "Solo los instructores pueden acceder a este recurso")
    return current_user
```

---

## 7. Servicio `user_service.py`

```python
"""
Module: services.user_service
Description: User CRUD operations and profile management
"""
import json
import pathlib
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.utils.security import hash_password
from app.utils.storage import get_avatar_path


def get_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def create(db: Session, payload: RegisterRequest) -> User:
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        account_type=payload.account_type
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_profile(db: Session, user: User, data: dict, avatar_bytes: bytes = None, avatar_ext: str = None) -> User:
    """Update user profile fields. Handles avatar upload."""
    for field, value in data.items():
        if value is not None and hasattr(user, field):
            setattr(user, field, value)

    if avatar_bytes and avatar_ext:
        avatar_path = get_avatar_path(user.id, avatar_ext)
        avatar_path.write_bytes(avatar_bytes)
        user.avatar_url = f"/storage/avatars/avatar_{user.id}{avatar_ext}"

    db.commit()
    db.refresh(user)
    return user
```

---

## 8. Dashboard Service

```python
"""
Module: services.dashboard_service
Description: Aggregated statistics and chart data for the user dashboard
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.analysis import Analysis
from app.models.discipline import Technique, Discipline
from app.models.gamification import UserBadge, Badge
from app.models.user import User
from app.schemas.dashboard import (
    DashboardResponse, ProgressResponse, HeatmapResponse,
    HeatmapEntry, ProgressDataset
)

BELT_XP = {"blanco": 0, "amarillo": 501, "naranja": 1501, "verde": 3001, "azul": 5001, "marron": 8001, "negro": 12001}
BELT_ORDER = list(BELT_XP.keys())
DISCIPLINE_COLORS = {"Muay Thai": "#dc2626", "BJJ": "#d4af37", "Boxeo": "#2563eb"}


def get_dashboard(db: Session, user: User) -> DashboardResponse:
    completed = db.query(Analysis).filter(
        Analysis.user_id == user.id,
        Analysis.status == "completed"
    ).all()

    total = len(completed)
    best = max((a.global_score for a in completed if a.global_score), default=None)
    avg = round(sum(a.global_score for a in completed if a.global_score) / total, 1) if total else None

    # Favorite discipline
    disc_counts: dict[str, int] = {}
    tech_counts: dict[str, int] = {}
    for a in completed:
        if a.technique:
            disc = a.technique.discipline.display_name
            tech = a.technique.display_name
            disc_counts[disc] = disc_counts.get(disc, 0) + 1
            tech_counts[tech] = tech_counts.get(tech, 0) + 1

    fav_disc = max(disc_counts, key=disc_counts.get) if disc_counts else None
    fav_tech = max(tech_counts, key=tech_counts.get) if tech_counts else None

    # Next belt
    belt_idx = BELT_ORDER.index(user.belt_level) if user.belt_level in BELT_ORDER else 0
    next_belt = BELT_ORDER[belt_idx + 1] if belt_idx < len(BELT_ORDER) - 1 else None
    xp_next = BELT_XP[next_belt] if next_belt else None

    # Recent badges (last 5)
    recent_ub = db.query(UserBadge).filter(UserBadge.user_id == user.id).order_by(
        UserBadge.earned_at.desc()
    ).limit(5).all()

    recent_badges = [
        {
            "badge_id": ub.badge_id,
            "display_name": ub.badge.display_name,
            "icon_name": ub.badge.icon_name,
            "level": ub.badge.level,
            "earned_at": ub.earned_at.isoformat()
        }
        for ub in recent_ub
    ]

    # Recent analyses (last 3)
    recent = db.query(Analysis).filter(
        Analysis.user_id == user.id,
        Analysis.status == "completed"
    ).order_by(Analysis.created_at.desc()).limit(3).all()

    recent_analyses = [
        {
            "id": a.id,
            "technique_display_name": a.technique.display_name if a.technique else "—",
            "discipline_name": a.technique.discipline.display_name if a.technique else "—",
            "global_score": a.global_score,
            "created_at": a.created_at.isoformat()
        }
        for a in recent
    ]

    return DashboardResponse(
        total_analyses=total, best_score=best, average_score=avg,
        favorite_discipline=fav_disc, most_analyzed_technique=fav_tech,
        xp=user.xp, belt_level=user.belt_level,
        xp_for_next_belt=xp_next, xp_next_belt_name=next_belt,
        current_streak=user.current_streak, max_streak=user.max_streak,
        streak_shields=user.streak_shields,
        recent_badges=recent_badges, recent_analyses=recent_analyses
    )


def get_progress(db: Session, user_id: int, discipline_id: int = None, days: int = 30) -> ProgressResponse:
    """Weekly average scores grouped by week for a progress chart."""
    cutoff = date.today() - timedelta(days=days)
    query = db.query(Analysis).filter(
        Analysis.user_id == user_id,
        Analysis.status == "completed",
        Analysis.created_at >= cutoff
    )
    if discipline_id:
        query = query.join(Technique).filter(Technique.discipline_id == discipline_id)

    analyses = query.order_by(Analysis.created_at).all()

    # Group by week
    from collections import defaultdict
    weekly: dict[str, list[float]] = defaultdict(list)
    for a in analyses:
        if a.global_score:
            week_label = a.created_at.strftime("%Y-%m-%d")
            weekly[week_label].append(a.global_score)

    labels = sorted(weekly.keys())
    data = [round(sum(weekly[l]) / len(weekly[l]), 1) for l in labels]

    # Determine discipline label
    if discipline_id:
        disc = db.query(Discipline).filter(Discipline.id == discipline_id).first()
        disc_name = disc.display_name if disc else "Todas"
    else:
        disc_name = "Todas"

    color = DISCIPLINE_COLORS.get(disc_name, "#dc2626")

    return ProgressResponse(
        labels=labels,
        datasets=[ProgressDataset(discipline=disc_name, discipline_id=discipline_id or 0, color=color, data=data)]
    )


def get_heatmap(db: Session, user_id: int) -> HeatmapResponse:
    """Returns daily analysis counts for the last 90 days."""
    cutoff = date.today() - timedelta(days=90)
    results = db.query(
        func.date(Analysis.created_at).label("day"),
        func.count(Analysis.id).label("count")
    ).filter(
        Analysis.user_id == user_id,
        Analysis.status == "completed",
        Analysis.created_at >= cutoff
    ).group_by(func.date(Analysis.created_at)).all()

    return HeatmapResponse(data=[HeatmapEntry(date=str(r.day), count=r.count) for r in results])
```

---

## 9. Criterios de Calidad del Backend

- [ ] `GET /health` responde 200 al primer arranque
- [ ] El seed se ejecuta automáticamente y `GET /disciplines` retorna 3 disciplinas
- [ ] `POST /auth/register` + `POST /auth/login` funcionan con token válido
- [ ] `POST /analysis` con un vídeo MP4 real de una persona retorna puntuaciones
- [ ] El vídeo overlay se genera en `storage/videos/user_{id}/overlay/`
- [ ] `GET /dashboard/me` retorna datos coherentes con los análisis realizados
- [ ] XP y cinturón se actualizan en BD tras cada análisis completado
- [ ] Los badges se otorgan cuando se cumplen sus condiciones
- [ ] Todos los endpoints protegidos retornan 401 sin token
- [ ] La contraseña no aparece en ninguna respuesta de la API
- [ ] Los endpoints de instructor retornan 403 para cuentas de alumno

✅ ENTREGABLE 6 COMPLETADO
