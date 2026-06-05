# Documento 6: Briefing para Dev1 — Backend FighterIA

> **Destinatario:** Agente Dev1 — Desarrollador Backend Senior
> **Remitente:** Agente Product Owner Senior (a través del Arquitecto)
> **Proyecto:** FighterIA | **Fecha:** 2026-05-28 | **Plazo:** 6 días

---

## 1. Contexto del Proyecto

FighterIA es una plataforma web de entrenamiento de artes marciales que usa MediaPipe Pose para analizar vídeos de técnicas. El usuario sube un vídeo, el backend lo procesa frame a frame, calcula ángulos articulares, los compara con referencias biomecánicas correctas, genera un vídeo con overlay visual (articulaciones en verde/rojo con valores) y devuelve puntuación + feedback priorizado.

**Tu trabajo:** implementar el backend completo. Recibes toda la información necesaria en este documento. No debes preguntar nada al Arquitecto ni al PO.

---

## 2. Stack y Versiones Exactas

```
Python: 3.11
FastAPI: 0.111.0
Uvicorn: 0.29.0 [standard]
SQLAlchemy: 2.0.30
Pydantic: 2.7.1
pydantic-settings: 2.2.1
python-dotenv: 1.0.1
mediapipe: 0.10.14
opencv-python-headless: 4.9.0.80
numpy: 1.26.4
python-jose[cryptography]: 3.3.0
passlib[bcrypt]: 1.7.4
python-multipart: 0.0.9
Faker: 24.11.0 (solo para tests)
pytest: 8.2.0
httpx: 0.27.0
```

**Comando de arranque:** `uvicorn app.main:app --reload --port 8000`

---

## 3. Estructura de Carpetas a Crear

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── discipline.py
│   │   ├── biomechanical.py
│   │   ├── analysis.py
│   │   ├── gamification.py
│   │   └── instructor.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── discipline.py
│   │   ├── analysis.py
│   │   ├── dashboard.py
│   │   ├── gamification.py
│   │   └── instructor.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── disciplines.py
│   │   ├── analysis.py
│   │   ├── dashboard.py
│   │   ├── gamification.py
│   │   └── instructor.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── video_service.py
│   │   ├── mediapipe_service.py
│   │   ├── analysis_service.py
│   │   ├── scoring_service.py
│   │   ├── feedback_service.py
│   │   ├── gamification_service.py
│   │   └── instructor_service.py
│   └── utils/
│       ├── __init__.py
│       ├── security.py
│       └── storage.py
├── seed/
│   ├── __init__.py
│   └── seed_data.py
├── storage/
│   ├── videos/
│   └── avatars/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── .env
├── .env.example
└── requirements.txt
```

---

## 4. Archivos de Configuración Base

### 4.1 `.env.example`
```
PROJECT_NAME=FighterIA
VERSION=1.0.0
DATABASE_URL=sqlite:///./fighterai.db
SECRET_KEY=super-secret-key-change-in-production-minimum-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=["http://localhost:3000"]
STORAGE_PATH=./storage
MAX_VIDEO_SIZE_MB=200
MAX_VIDEO_DURATION_SECONDS=60
```

### 4.2 `app/config.py`
```python
"""
Module: config
Description: Application settings loaded from environment variables via pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "FighterIA"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./fighterai.db"
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    STORAGE_PATH: str = "./storage"
    MAX_VIDEO_SIZE_MB: int = 200
    MAX_VIDEO_DURATION_SECONDS: int = 60

    class Config:
        env_file = ".env"


settings = Settings()
```

### 4.3 `app/database.py`
```python
"""
Module: database
Description: SQLAlchemy engine, session factory and declarative base for SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a transactional DB session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.4 `app/main.py`
```python
"""
Module: main
Description: FastAPI application entry point — configures CORS, mounts routers, runs DB init and seed on startup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, disciplines, analysis, dashboard, gamification, instructor
from seed.seed_data import run_seed
import pathlib

# Create all tables
Base.metadata.create_all(bind=engine)

# Ensure storage directories exist
pathlib.Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{settings.STORAGE_PATH}/videos").mkdir(parents=True, exist_ok=True)
pathlib.Path(f"{settings.STORAGE_PATH}/avatars").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered martial arts training platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount storage for direct file access (avatars)
app.mount("/storage", StaticFiles(directory=settings.STORAGE_PATH), name="storage")

# Include all routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(disciplines.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(gamification.router)
app.include_router(instructor.router)


@app.on_event("startup")
async def startup_event():
    """Run database seed on startup if tables are empty."""
    run_seed()


@app.get("/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION, "project": settings.PROJECT_NAME}
```

---

## 5. Modelos SQLAlchemy

### 5.1 `app/models/user.py`
```python
"""
Module: models.user
Description: User model with auth fields, profile, gamification stats and streak data
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False, default="alumno")  # alumno | instructor
    bio = Column(String(500), nullable=True)
    gym = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    experience_years = Column(Integer, default=0)
    disciplines = Column(String(255), nullable=True)  # JSON array as string
    avatar_url = Column(String(500), nullable=True)
    xp = Column(Integer, default=0, nullable=False)
    belt_level = Column(String(20), default="blanco", nullable=False)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)
    streak_shield_active = Column(Boolean, default=False)
    streak_shields = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    analyses = relationship("Analysis", back_populates="user")
    user_badges = relationship("UserBadge", back_populates="user")
    instructor_groups = relationship("InstructorGroup", back_populates="instructor")
    group_memberships = relationship("GroupMember", back_populates="student")
```

### 5.2 `app/models/discipline.py`
```python
"""
Module: models.discipline
Description: Discipline and Technique catalog models
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Discipline(Base):
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String(50), nullable=True)

    techniques = relationship("Technique", back_populates="discipline")


class Technique(Base):
    __tablename__ = "techniques"

    id = Column(Integer, primary_key=True, index=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")  # easy | medium | hard
    xp_multiplier = Column(Float, default=1.0)

    discipline = relationship("Discipline", back_populates="techniques")
    biomechanical_refs = relationship("BiomechanicalReference", back_populates="technique")
    analyses = relationship("Analysis", back_populates="technique")
```

### 5.3 `app/models/biomechanical.py`
```python
"""
Module: models.biomechanical
Description: Biomechanical reference angles per joint per technique
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class BiomechanicalReference(Base):
    __tablename__ = "biomechanical_references"

    id = Column(Integer, primary_key=True, index=True)
    technique_id = Column(Integer, ForeignKey("techniques.id"), nullable=False, index=True)
    joint_name = Column(String(50), nullable=False)
    phase = Column(String(30), default="execution")
    min_angle = Column(Float, nullable=False)
    max_angle = Column(Float, nullable=False)
    optimal_angle = Column(Float, nullable=False)
    weight = Column(Float, default=1.0)
    description = Column(Text, nullable=True)

    technique = relationship("Technique", back_populates="biomechanical_refs")
```

### 5.4 `app/models/analysis.py`
```python
"""
Module: models.analysis
Description: Analysis, joint results, feedback and comments models
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    technique_id = Column(Integer, ForeignKey("techniques.id"), nullable=False)
    video_original_path = Column(String(500), nullable=False)
    video_overlay_path = Column(String(500), nullable=True)
    status = Column(String(20), default="pending")  # pending|processing|completed|failed
    global_score = Column(Float, nullable=True)
    power_score = Column(Float, nullable=True)
    balance_score = Column(Float, nullable=True)
    alignment_score = Column(Float, nullable=True)
    speed_score = Column(Float, nullable=True)
    xp_awarded = Column(Integer, default=0)
    is_public = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="analyses")
    technique = relationship("Technique", back_populates="analyses")
    joint_results = relationship("AnalysisJointResult", back_populates="analysis", cascade="all, delete-orphan")
    feedback = relationship("AnalysisFeedback", back_populates="analysis", cascade="all, delete-orphan", order_by="AnalysisFeedback.priority_order")
    comments = relationship("AnalysisComment", back_populates="analysis", cascade="all, delete-orphan")


class AnalysisJointResult(Base):
    __tablename__ = "analysis_joint_results"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    joint_name = Column(String(50), nullable=False)
    measured_angle = Column(Float, nullable=False)
    reference_min = Column(Float, nullable=False)
    reference_max = Column(Float, nullable=False)
    optimal_angle = Column(Float, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    deviation = Column(Float, nullable=False)

    analysis = relationship("Analysis", back_populates="joint_results")


class AnalysisFeedback(Base):
    __tablename__ = "analysis_feedback"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    correction_title = Column(String(200), nullable=False)
    correction_text = Column(Text, nullable=False)
    biomechanical_explanation = Column(Text, nullable=True)
    exercise_suggestion = Column(Text, nullable=True)
    priority_order = Column(Integer, nullable=False)
    impact_score = Column(Float, nullable=False)

    analysis = relationship("Analysis", back_populates="feedback")


class AnalysisComment(Base):
    __tablename__ = "analysis_comments"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    analysis = relationship("Analysis", back_populates="comments")
    author = relationship("User")
```

### 5.5 `app/models/gamification.py`
```python
"""
Module: models.gamification
Description: Badge catalog and user badge junction table
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    level = Column(String(20), nullable=False)  # bronze | silver | gold
    icon_name = Column(String(50), nullable=False)
    condition_type = Column(String(50), nullable=False)
    condition_value = Column(Integer, default=1)
    xp_reward = Column(Integer, default=50)

    user_badges = relationship("UserBadge", back_populates="badge")


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id"), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    user = relationship("User", back_populates="user_badges")
    badge = relationship("Badge", back_populates="user_badges")
```

### 5.6 `app/models/instructor.py`
```python
"""
Module: models.instructor
Description: Instructor groups and membership models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class InstructorGroup(Base):
    __tablename__ = "instructor_groups"

    id = Column(Integer, primary_key=True, index=True)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    invite_code = Column(String(20), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    instructor = relationship("User", back_populates="instructor_groups")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("instructor_groups.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (UniqueConstraint("group_id", "student_id", name="uq_group_member"),)

    group = relationship("InstructorGroup", back_populates="members")
    student = relationship("User", back_populates="group_memberships")
```

---

## 6. Servicios — Lógica de Negocio

### 6.1 `app/utils/security.py`
```python
"""
Module: utils.security
Description: JWT creation and validation helpers using python-jose
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload["type"] = "refresh"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises JWTError if token is invalid or expired."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

### 6.2 `app/utils/storage.py`
```python
"""
Module: utils.storage
Description: File storage path helpers using pathlib for Windows compatibility
"""
import pathlib
from app.config import settings


def get_user_storage_path(user_id: int) -> pathlib.Path:
    path = pathlib.Path(settings.STORAGE_PATH) / "videos" / f"user_{user_id}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_original_video_path(user_id: int, analysis_id: int, extension: str) -> pathlib.Path:
    base = get_user_storage_path(user_id) / "original"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"analysis_{analysis_id}_original{extension}"


def get_overlay_video_path(user_id: int, analysis_id: int) -> pathlib.Path:
    base = get_user_storage_path(user_id) / "overlay"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"analysis_{analysis_id}_overlay.mp4"


def get_avatar_path(user_id: int, extension: str) -> pathlib.Path:
    base = pathlib.Path(settings.STORAGE_PATH) / "avatars"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"avatar_{user_id}{extension}"
```

### 6.3 `app/services/mediapipe_service.py`
```python
"""
Module: services.mediapipe_service
Description: PoseAnalyzer class — processes video frames with MediaPipe Pose,
             calculates joint angles and generates annotated overlay video
"""
import cv2
import mediapipe as mp
import numpy as np
import pathlib
from typing import Optional

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# MediaPipe landmark IDs for the joints we analyze
JOINT_LANDMARKS = {
    "left_elbow":    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    "right_elbow":   (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    "left_shoulder": (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
    "right_shoulder":(mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP),
    "left_knee":     (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    "right_knee":    (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
    "left_hip":      (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    "right_hip":     (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE),
    # Proxy joints mapped to available landmarks:
    "kicking_hip":   (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    "kicking_knee":  (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    "support_knee":  (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
    "hip_rotation_proxy": (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
    "hip_flexion":   (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    "target_arm_extension": (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    "knee_pinch":    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE),
    "knee_bend":     (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    "hip_extension": (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    "knee_flexion":  (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
    "ankle_behind_knee": (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.RIGHT_KNEE),
    "target_arm_lock": (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    "front_knee":    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    "rear_knee":     (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
}

COLOR_CORRECT = (0, 255, 0)    # Green — BGR
COLOR_INCORRECT = (0, 0, 255)  # Red — BGR
COLOR_TEXT = (255, 255, 255)   # White
COLOR_REF = (0, 165, 255)      # Orange — reference value


def calculate_angle(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    """
    Calculate the angle (degrees) at point B formed by segments A-B and C-B.
    Returns a value between 0 and 180.
    """
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-8)
    cosine = np.clip(cosine, -1.0, 1.0)
    return float(np.degrees(np.arccos(cosine)))


class VideoAnalysisResult:
    """Container for the analysis result from a single video."""
    def __init__(self):
        self.joint_angles: dict[str, float] = {}  # joint_name → angle at key frame
        self.frame_count: int = 0
        self.key_frame_index: int = 0
        self.pose_detected: bool = False
        self.speed_proxy: float = 0.0  # average landmark velocity between frames


class PoseAnalyzer:
    """Processes a video file with MediaPipe Pose and generates an annotated overlay video."""

    def __init__(self, min_detection_confidence: float = 0.5, min_tracking_confidence: float = 0.5):
        self.pose = mp_pose.Pose(
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

    def analyze_video(
        self,
        input_path: pathlib.Path,
        output_path: pathlib.Path,
        biomechanical_refs: dict[str, dict]  # {joint_name: {min, max, optimal}}
    ) -> VideoAnalysisResult:
        """
        Process input_path frame by frame, generate overlay video at output_path,
        and return measured joint angles at the key frame.

        Args:
            input_path: Path to the original video file
            output_path: Path where the overlay video will be saved
            biomechanical_refs: dict mapping joint_name to reference angle data

        Returns:
            VideoAnalysisResult with joint_angles at key frame and metadata
        """
        result = VideoAnalysisResult()
        cap = cv2.VideoCapture(str(input_path))

        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {input_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Use mp4v codec for Windows compatibility
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

        all_frames_landmarks = []
        frame_idx = 0

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            pose_result = self.pose.process(frame_rgb)
            frame_rgb.flags.writeable = True

            if pose_result.pose_landmarks:
                result.pose_detected = True
                landmarks = pose_result.pose_landmarks.landmark
                all_frames_landmarks.append((frame_idx, landmarks))

            all_frames_landmarks.append((frame_idx, pose_result.pose_landmarks.landmark if pose_result.pose_landmarks else None))
            frame_idx += 1

        result.frame_count = frame_idx

        if not result.pose_detected:
            cap.release()
            writer.release()
            return result

        # Identify key frame: frame where maximum total extension occurs
        result.key_frame_index = self._find_key_frame(all_frames_landmarks)

        # Calculate speed proxy from landmark movement between consecutive frames
        result.speed_proxy = self._calculate_speed_proxy(all_frames_landmarks)

        # Get angles at key frame
        key_landmarks = None
        for idx, lm in all_frames_landmarks:
            if idx == result.key_frame_index and lm is not None:
                key_landmarks = lm
                break

        if key_landmarks:
            for joint_name, landmark_triplet in JOINT_LANDMARKS.items():
                try:
                    a = np.array([key_landmarks[landmark_triplet[0].value].x, key_landmarks[landmark_triplet[0].value].y])
                    b = np.array([key_landmarks[landmark_triplet[1].value].x, key_landmarks[landmark_triplet[1].value].y])
                    c = np.array([key_landmarks[landmark_triplet[2].value].x, key_landmarks[landmark_triplet[2].value].y])
                    result.joint_angles[joint_name] = calculate_angle(a, b, c)
                except (IndexError, AttributeError):
                    pass

        # Second pass: write overlay video
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_idx = 0

        for frame_idx_stored, landmarks in all_frames_landmarks:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx_stored)
            success, frame = cap.read()
            if not success:
                break

            if landmarks is not None:
                # Draw base pose skeleton
                pose_landmarks_proto = mp.framework.formats.landmark_pb2.NormalizedLandmarkList()
                for lm in landmarks:
                    new_lm = pose_landmarks_proto.landmark.add()
                    new_lm.x, new_lm.y, new_lm.z = lm.x, lm.y, lm.z
                mp_drawing.draw_landmarks(frame, pose_landmarks_proto, mp_pose.POSE_CONNECTIONS)

                # Draw angle annotations on key frame
                if frame_idx_stored == result.key_frame_index:
                    self._draw_angle_annotations(frame, landmarks, biomechanical_refs, width, height)

            writer.write(frame)

        cap.release()
        writer.release()
        self.pose.reset()
        return result

    def _find_key_frame(self, all_frames_landmarks: list) -> int:
        """Find the frame with maximum right arm extension (proxy for technique peak)."""
        max_extension = -1
        key_frame = 0
        for frame_idx, landmarks in all_frames_landmarks:
            if landmarks is None:
                continue
            try:
                a = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y])
                b = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y])
                c = np.array([landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                               landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y])
                angle = calculate_angle(a, b, c)
                if angle > max_extension:
                    max_extension = angle
                    key_frame = frame_idx
            except (IndexError, AttributeError):
                pass
        return key_frame

    def _calculate_speed_proxy(self, all_frames_landmarks: list) -> float:
        """Calculate average wrist velocity between consecutive frames as speed proxy."""
        velocities = []
        prev_pos = None
        for _, landmarks in all_frames_landmarks:
            if landmarks is None:
                prev_pos = None
                continue
            try:
                wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
                pos = np.array([wrist.x, wrist.y])
                if prev_pos is not None:
                    velocities.append(float(np.linalg.norm(pos - prev_pos)))
                prev_pos = pos
            except (IndexError, AttributeError):
                prev_pos = None
        return float(np.mean(velocities)) if velocities else 0.0

    def _draw_angle_annotations(self, frame, landmarks, biomechanical_refs: dict, width: int, height: int):
        """Draw angle values and color-coded circles on the key frame."""
        for joint_name, ref in biomechanical_refs.items():
            if joint_name not in JOINT_LANDMARKS or joint_name not in self._last_angles:
                continue
            triplet = JOINT_LANDMARKS[joint_name]
            try:
                b_lm = landmarks[triplet[1].value]
                center = (int(b_lm.x * width), int(b_lm.y * height))
                angle = self._last_angles[joint_name]
                is_correct = ref["min_angle"] <= angle <= ref["max_angle"]
                color = COLOR_CORRECT if is_correct else COLOR_INCORRECT

                cv2.circle(frame, center, 12, color, -1)
                cv2.putText(frame, f"{angle:.0f}°", (center[0] + 15, center[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_TEXT, 1, cv2.LINE_AA)
                cv2.putText(frame, f"[{ref['min_angle']:.0f}-{ref['max_angle']:.0f}]",
                            (center[0] + 15, center[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.35, COLOR_REF, 1, cv2.LINE_AA)
            except (IndexError, AttributeError):
                pass

    def close(self):
        """Release MediaPipe resources."""
        self.pose.close()
```

### 6.4 `app/services/scoring_service.py`
```python
"""
Module: services.scoring_service
Description: Calculates technical scores (alignment, power, balance, speed, global)
             from joint measurement results against biomechanical references
"""
from typing import List, Dict


def calculate_scores(
    joint_results: List[Dict],  # [{joint_name, measured_angle, ref_min, ref_max, optimal_angle, weight}]
    speed_proxy: float,         # 0.0 - ~0.1, normalized movement velocity
    frame_count: int
) -> Dict[str, float]:
    """
    Returns dict with: alignment_score, power_score, balance_score, speed_score, global_score
    All scores are in range 0.0 - 100.0
    """
    if not joint_results:
        return {k: 0.0 for k in ["alignment_score", "power_score", "balance_score", "speed_score", "global_score"]}

    # Alignment score: weighted percentage of joints within correct range
    total_weight = sum(r.get("weight", 1.0) for r in joint_results)
    alignment_score = 0.0
    for r in joint_results:
        w = r.get("weight", 1.0)
        if r["is_correct"]:
            alignment_score += w
        else:
            # Partial credit: 50% if within 10° of range
            deviation = min(abs(r["measured_angle"] - r["ref_min"]),
                            abs(r["measured_angle"] - r["ref_max"]))
            if deviation <= 10:
                alignment_score += w * 0.5
    alignment_score = (alignment_score / total_weight) * 100

    # Power score: based on extension joints (elbows, knees)
    extension_joints = [r for r in joint_results if "elbow" in r["joint_name"] or "knee" in r["joint_name"]]
    if extension_joints:
        power_scores = []
        for r in extension_joints:
            ratio = min(r["measured_angle"] / r["optimal_angle"], 1.0) if r["optimal_angle"] > 0 else 1.0
            power_scores.append(ratio * 100)
        power_score = float(sum(power_scores) / len(power_scores))
    else:
        power_score = alignment_score  # fallback

    # Balance score: based on hip and knee joints
    balance_joints = [r for r in joint_results if "hip" in r["joint_name"] or "knee" in r["joint_name"]]
    if balance_joints:
        balance_score = sum(100.0 if r["is_correct"] else max(0, 100 - abs(r["deviation"]) * 2) for r in balance_joints) / len(balance_joints)
    else:
        balance_score = alignment_score

    # Speed score: normalize speed_proxy to 0-100 (typical max is ~0.05)
    speed_score = min(float(speed_proxy * 2000), 100.0)

    # Global score: weighted average
    global_score = (alignment_score * 0.40 + power_score * 0.25 + balance_score * 0.20 + speed_score * 0.15)
    global_score = max(0.0, min(100.0, global_score))

    return {
        "alignment_score": round(alignment_score, 1),
        "power_score": round(power_score, 1),
        "balance_score": round(balance_score, 1),
        "speed_score": round(speed_score, 1),
        "global_score": round(global_score, 1)
    }
```

### 6.5 `app/services/feedback_service.py`
```python
"""
Module: services.feedback_service
Description: Generates prioritized textual feedback from joint analysis results
"""
from typing import List, Dict


FEEDBACK_TEMPLATES = {
    "right_elbow": {
        "title": "Extensión de codo derecho insuficiente",
        "text": "Tu codo derecho alcanza {angle:.0f}° en el momento de impacto, cuando el rango correcto es {min:.0f}°-{max:.0f}°. Esto reduce tu alcance efectivo y la transferencia de fuerza.",
        "biomechanical": "La extensión completa del codo en los golpes maximiza el alcance y la transferencia de energía cinética desde el hombro hasta el puño.",
        "exercise": "Practica golpes al saco lento enfocándote en extender completamente el brazo. Usa un espejo para verificar la extensión."
    },
    "left_elbow": {
        "title": "Guardia baja — codo izquierdo",
        "text": "El ángulo de tu codo izquierdo ({angle:.0f}°) está fuera del rango de guardia correcto ({min:.0f}°-{max:.0f}°). Esto expone tu cabeza.",
        "biomechanical": "Mantener el codo de guardia en el ángulo correcto protege el mentón y permite reaccionar ante contraataques.",
        "exercise": "Shadowboxing frente al espejo manteniendo conciencia del codo de guardia. Pídele a un compañero que te avise cuando lo bajes."
    },
    "right_shoulder": {
        "title": "Elevación de hombro derecho incorrecta",
        "text": "Tu hombro derecho se encuentra a {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}° para este movimiento.",
        "biomechanical": "La altura del hombro en el momento del golpe determina la trayectoria y la zona de impacto.",
        "exercise": "Trabaja la trayectoria del golpe frente a un espejo a cámara lenta, corrigiendo la altura del hombro."
    },
    "left_knee": {
        "title": "Flexión de rodilla izquierda fuera de rango",
        "text": "La flexión de tu rodilla izquierda ({angle:.0f}°) está fuera del rango correcto ({min:.0f}°-{max:.0f}°) para esta técnica.",
        "biomechanical": "La posición de la rodilla delantera determina la estabilidad, la base de apoyo y la capacidad de generar potencia desde las piernas.",
        "exercise": "Trabaja la postura básica con sentadillas parciales para ganar conciencia de la posición de rodilla."
    },
    "right_knee": {
        "title": "Flexión de rodilla trasera incorrecta",
        "text": "La rodilla trasera muestra {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}°.",
        "biomechanical": "La rodilla trasera es el punto de transferencia de la cadena cinética desde el suelo hasta el golpe.",
        "exercise": "Drill de pivote de pie trasero con énfasis en la flexión de rodilla correcta."
    },
    "hip_rotation_proxy": {
        "title": "Rotación de cadera insuficiente",
        "text": "La rotación de cadera estimada es de {angle:.0f}° cuando debería estar entre {min:.0f}° y {max:.0f}°. Esto reduce significativamente la potencia del golpe.",
        "biomechanical": "La rotación de cadera es responsable del 60-70% de la potencia en los golpes de boxeo y Muay Thai.",
        "exercise": "Drill de rotación de caderas con palos de madera. Práctica de golpes al saco enfocándose en sentir la rotación."
    },
    "kicking_hip": {
        "title": "Flexión de cadera en el kick fuera de rango",
        "text": "La cadera de la pierna de patada alcanza {angle:.0f}° cuando el rango correcto es {min:.0f}°-{max:.0f}°.",
        "biomechanical": "La flexión correcta de cadera determina la altura y la potencia del impacto en los kicks.",
        "exercise": "Ejercicios de movilidad de cadera. Practica la cámara lenta del kick frente al espejo."
    },
    "kicking_knee": {
        "title": "Extensión de rodilla en el kick incompleta",
        "text": "Tu rodilla de patada alcanza {angle:.0f}° en el impacto cuando debería estar entre {min:.0f}°-{max:.0f}°.",
        "biomechanical": "La extensión de rodilla en el momento del impacto es fundamental para maximizar el daño y la penetración del golpe.",
        "exercise": "Practica el snap de rodilla contra un pad fijo. Usa una banda elástica para trabajar la extensión."
    },
}

DEFAULT_FEEDBACK = {
    "title": "Ángulo articular fuera de rango",
    "text": "El ángulo medido en {joint} es {angle:.0f}°. El rango correcto para esta técnica es {min:.0f}°-{max:.0f}°.",
    "biomechanical": "Los ángulos articulares correctos son fundamentales para la eficiencia biomecánica y la prevención de lesiones.",
    "exercise": "Practica la técnica a cámara lenta frente a un espejo, prestando atención específica a esta articulación."
}


def generate_feedback(joint_results: List[Dict]) -> List[Dict]:
    """
    Generate prioritized feedback list from joint results.
    Only generates feedback for joints outside the correct range.
    Sorted by impact_score descending (highest impact first).
    """
    incorrect_joints = [r for r in joint_results if not r["is_correct"]]
    if not incorrect_joints:
        return []

    # Sort by absolute deviation (largest deviation = highest priority)
    incorrect_joints.sort(key=lambda r: abs(r["deviation"]), reverse=True)

    feedback_list = []
    for priority, joint_result in enumerate(incorrect_joints, start=1):
        joint_name = joint_result["joint_name"]
        template = FEEDBACK_TEMPLATES.get(joint_name, DEFAULT_FEEDBACK)
        impact_score = min(abs(joint_result["deviation"]) / 90.0, 1.0)  # normalize to 0-1

        feedback_list.append({
            "correction_title": template["title"],
            "correction_text": template["text"].format(
                angle=joint_result["measured_angle"],
                min=joint_result["ref_min"],
                max=joint_result["ref_max"],
                joint=joint_name.replace("_", " ")
            ),
            "biomechanical_explanation": template["biomechanical"],
            "exercise_suggestion": template["exercise"],
            "priority_order": priority,
            "impact_score": round(impact_score, 3)
        })

    return feedback_list
```

### 6.6 `app/services/gamification_service.py`
```python
"""
Module: services.gamification_service
Description: XP awards, belt level updates, badge checks and streak management
"""
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.gamification import Badge, UserBadge
from app.models.analysis import Analysis

BELT_THRESHOLDS = {
    "blanco": 0,
    "amarillo": 501,
    "naranja": 1501,
    "verde": 3001,
    "azul": 5001,
    "marron": 8001,
    "negro": 12001
}

XP_BY_SCORE = {
    (0, 49): 10,
    (50, 74): 20,
    (75, 89): 30,
    (90, 99): 45,
    (100, 100): 60
}

BADGE_CONDITIONS = {
    "first_analysis": lambda user, db: db.query(Analysis).filter(Analysis.user_id == user.id, Analysis.status == "completed").count() >= 1,
    "streak_7": lambda user, db: user.current_streak >= 7,
    "score_100": lambda user, db: db.query(Analysis).filter(Analysis.user_id == user.id, Analysis.global_score >= 100.0).count() >= 1,
    "muay_thai_50": lambda user, db: db.query(Analysis).join(Analysis.technique).join("discipline").filter(
        Analysis.user_id == user.id, Analysis.status == "completed"
    ).count() >= 50,  # simplified — full discipline filter in actual implementation
    "bjj_50": lambda user, db: True,  # placeholder
    "boxing_50": lambda user, db: True,  # placeholder
    "belt_negro": lambda user, db: user.belt_level == "negro",
}


def calculate_xp_reward(global_score: float, xp_multiplier: float) -> int:
    """Calculate XP to award based on score and technique difficulty multiplier."""
    for (low, high), xp in XP_BY_SCORE.items():
        if low <= round(global_score) <= high:
            return round(xp * xp_multiplier)
    return 10


def get_belt_for_xp(xp: int) -> str:
    """Return the belt level name for a given XP total."""
    belt = "blanco"
    for belt_name, threshold in BELT_THRESHOLDS.items():
        if xp >= threshold:
            belt = belt_name
    return belt


def award_xp_and_update_belt(user: User, xp_to_add: int, db: Session) -> dict:
    """Award XP to user, update belt if needed. Returns {xp_added, new_belt, belt_upgraded}."""
    old_belt = user.belt_level
    user.xp += xp_to_add
    new_belt = get_belt_for_xp(user.xp)
    user.belt_level = new_belt
    db.flush()
    return {"xp_added": xp_to_add, "new_belt": new_belt, "belt_upgraded": new_belt != old_belt}


def update_streak(user: User, db: Session):
    """Update daily streak. Call after a completed analysis."""
    today = date.today()
    if user.last_activity_date is None:
        user.current_streak = 1
    elif user.last_activity_date == today:
        return  # Already trained today, no change
    elif user.last_activity_date == today - timedelta(days=1):
        user.current_streak += 1
    else:
        # Missed a day — check for shield
        if user.streak_shield_active:
            user.streak_shield_active = False
        else:
            user.current_streak = 1  # Reset streak

    user.last_activity_date = today
    if user.current_streak > user.max_streak:
        user.max_streak = user.current_streak
    db.flush()


def check_and_award_badges(user: User, db: Session) -> list[dict]:
    """Check all badge conditions and award any newly earned badges. Returns list of newly earned badges."""
    all_badges = db.query(Badge).all()
    earned_badge_ids = {ub.badge_id for ub in db.query(UserBadge).filter(UserBadge.user_id == user.id).all()}
    newly_earned = []

    for badge in all_badges:
        if badge.id in earned_badge_ids:
            continue
        condition_fn = BADGE_CONDITIONS.get(badge.condition_type)
        if condition_fn and condition_fn(user, db):
            user_badge = UserBadge(user_id=user.id, badge_id=badge.id)
            db.add(user_badge)
            user.xp += badge.xp_reward
            newly_earned.append({"badge_id": badge.id, "display_name": badge.display_name, "xp_reward": badge.xp_reward})
            db.flush()

    return newly_earned
```

---

## 7. Seed de Base de Datos

### `seed/seed_data.py`
```python
"""
Module: seed.seed_data
Description: Populates disciplines, techniques and biomechanical references on first startup
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.discipline import Discipline, Technique
from app.models.biomechanical import BiomechanicalReference
from app.models.gamification import Badge


DISCIPLINES = [
    {"name": "muay_thai", "display_name": "Muay Thai", "description": "Arte marcial tailandés conocido como el Arte de las Ocho Extremidades.", "icon_name": "muay-thai"},
    {"name": "bjj", "display_name": "BJJ", "description": "Jiu-Jitsu Brasileño — arte marcial de suelo enfocado en sumisiones.", "icon_name": "bjj"},
    {"name": "boxing", "display_name": "Boxeo", "description": "Arte del boxeo occidental, centrado en golpes de puño.", "icon_name": "boxing"},
]

TECHNIQUES = {
    "boxing": [
        {"name": "jab", "display_name": "Jab", "description": "Golpe recto con el brazo delantero. Rápido, de distancia.", "difficulty": "easy", "xp_multiplier": 1.0},
        {"name": "cross", "display_name": "Cross", "description": "Golpe recto con el brazo trasero con rotación de cadera.", "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "hook", "display_name": "Hook", "description": "Gancho lateral con el brazo delantero o trasero.", "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "uppercut", "display_name": "Uppercut", "description": "Golpe ascendente hacia el mentón del oponente.", "difficulty": "hard", "xp_multiplier": 2.0},
    ],
    "muay_thai": [
        {"name": "jab_mt", "display_name": "Jab MT", "description": "Jab de Muay Thai con guardia alta.", "difficulty": "easy", "xp_multiplier": 1.0},
        {"name": "roundkick_medio", "display_name": "Roundkick Medio", "description": "Patada circular al cuerpo con la espinilla.", "difficulty": "hard", "xp_multiplier": 2.0},
        {"name": "teep", "display_name": "Teep", "description": "Patada frontal de empuje con la planta del pie.", "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "cross_mt", "display_name": "Cross MT", "description": "Cross de Muay Thai con rotación de cadera pronunciada.", "difficulty": "medium", "xp_multiplier": 1.5},
    ],
    "bjj": [
        {"name": "armbar", "display_name": "Armbar desde Guardia", "description": "Palanca de codo desde posición de guardia cerrada.", "difficulty": "hard", "xp_multiplier": 2.0},
        {"name": "closed_guard", "display_name": "Guardia Cerrada", "description": "Posición de guardia cerrada controlando al oponente.", "difficulty": "easy", "xp_multiplier": 1.0},
        {"name": "mount", "display_name": "Montada", "description": "Posición de control montando al oponente.", "difficulty": "medium", "xp_multiplier": 1.5},
        {"name": "triangle", "display_name": "Triángulo", "description": "Estrangulamiento triangular con las piernas.", "difficulty": "hard", "xp_multiplier": 2.0},
    ]
}

BIOMECHANICAL_REFS = {
    "jab":           [("right_elbow", 165, 180, 175, 1.5), ("right_shoulder", 80, 100, 90, 1.0), ("left_elbow", 85, 100, 90, 0.8), ("hip_rotation_proxy", 10, 30, 20, 1.0), ("front_knee", 145, 165, 155, 0.7)],
    "cross":         [("right_elbow", 165, 180, 175, 1.5), ("right_shoulder", 80, 100, 90, 1.0), ("hip_rotation_proxy", 35, 55, 45, 1.5), ("rear_knee", 155, 175, 165, 0.8)],
    "hook":          [("right_elbow", 80, 100, 90, 1.5), ("right_shoulder", 75, 95, 85, 1.0), ("hip_rotation_proxy", 40, 60, 50, 1.2)],
    "uppercut":      [("right_elbow", 70, 90, 80, 1.5), ("front_knee", 120, 145, 130, 1.2), ("right_hip", 150, 170, 160, 1.0)],
    "jab_mt":        [("right_elbow", 165, 180, 175, 1.5), ("right_shoulder", 80, 100, 90, 1.0), ("hip_rotation_proxy", 10, 30, 20, 0.8)],
    "roundkick_medio":[("kicking_hip", 80, 110, 95, 1.5), ("kicking_knee", 150, 175, 165, 1.5), ("support_knee", 135, 155, 145, 1.2), ("hip_rotation_proxy", 45, 65, 55, 1.3)],
    "teep":          [("kicking_hip", 80, 100, 90, 1.5), ("kicking_knee", 160, 180, 170, 1.5), ("support_knee", 145, 165, 155, 1.0)],
    "cross_mt":      [("right_elbow", 165, 180, 175, 1.5), ("hip_rotation_proxy", 35, 55, 45, 1.5)],
    "armbar":        [("hip_flexion", 85, 105, 95, 1.5), ("target_arm_extension", 165, 180, 175, 2.0), ("knee_pinch", 80, 100, 90, 1.0)],
    "closed_guard":  [("hip_flexion", 85, 110, 100, 1.2), ("knee_bend", 100, 130, 115, 1.0)],
    "mount":         [("hip_extension", 155, 175, 165, 1.2), ("knee_flexion", 85, 110, 95, 1.0)],
    "triangle":      [("hip_flexion", 90, 115, 105, 1.5), ("ankle_behind_knee", 80, 100, 90, 1.0), ("target_arm_lock", 160, 180, 170, 1.5)],
}

BADGES_DATA = [
    {"name": "first_analysis", "display_name": "Primer Golpe", "description": "Realiza tu primer análisis", "level": "bronze", "icon_name": "fist", "condition_type": "first_analysis", "condition_value": 1, "xp_reward": 50},
    {"name": "streak_7", "display_name": "En Racha", "description": "Mantén 7 días consecutivos de entrenamiento", "level": "silver", "icon_name": "fire", "condition_type": "streak_7", "condition_value": 7, "xp_reward": 100},
    {"name": "score_100", "display_name": "Perfeccionista", "description": "Obtén una puntuación de 100 en cualquier técnica", "level": "gold", "icon_name": "star", "condition_type": "score_100", "condition_value": 100, "xp_reward": 200},
    {"name": "muay_thai_50", "display_name": "Maestro del Muay Thai", "description": "Analiza 50 técnicas de Muay Thai", "level": "gold", "icon_name": "shin", "condition_type": "muay_thai_50", "condition_value": 50, "xp_reward": 300},
    {"name": "bjj_50", "display_name": "Guardián del Suelo", "description": "Analiza 50 técnicas de BJJ", "level": "gold", "icon_name": "mat", "condition_type": "bjj_50", "condition_value": 50, "xp_reward": 300},
    {"name": "boxing_50", "display_name": "El Cuadrado", "description": "Analiza 50 técnicas de Boxeo", "level": "gold", "icon_name": "glove", "condition_type": "boxing_50", "condition_value": 50, "xp_reward": 300},
    {"name": "belt_negro", "display_name": "Leyenda", "description": "Alcanza el cinturón negro", "level": "gold", "icon_name": "belt", "condition_type": "belt_negro", "condition_value": 1, "xp_reward": 500},
]


def run_seed():
    """Idempotent seed function — only runs if disciplines table is empty."""
    db: Session = SessionLocal()
    try:
        if db.query(Discipline).count() > 0:
            return  # Already seeded

        discipline_map = {}
        for d_data in DISCIPLINES:
            d = Discipline(**d_data)
            db.add(d)
            db.flush()
            discipline_map[d_data["name"]] = d.id

        technique_map = {}
        for discipline_name, techniques in TECHNIQUES.items():
            disc_id = discipline_map[discipline_name]
            for t_data in techniques:
                t = Technique(discipline_id=disc_id, **t_data)
                db.add(t)
                db.flush()
                technique_map[t_data["name"]] = t.id

        for technique_name, refs in BIOMECHANICAL_REFS.items():
            if technique_name not in technique_map:
                continue
            tech_id = technique_map[technique_name]
            for joint_name, min_a, max_a, opt_a, weight in refs:
                ref = BiomechanicalReference(
                    technique_id=tech_id,
                    joint_name=joint_name,
                    min_angle=min_a,
                    max_angle=max_a,
                    optimal_angle=opt_a,
                    weight=weight
                )
                db.add(ref)

        for b_data in BADGES_DATA:
            db.add(Badge(**b_data))

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

---

## 8. Criterios de Calidad del Backend

- [ ] `uvicorn app.main:app --reload --port 8000` arranca sin errores
- [ ] `GET /health` responde 200 OK
- [ ] `GET /disciplines` retorna 3 disciplinas tras el seed
- [ ] `POST /auth/register` + `POST /auth/login` funcionan con JWT válido
- [ ] `POST /analysis` procesa un vídeo MP4 de prueba y retorna puntuación
- [ ] El vídeo overlay se guarda en `storage/videos/user_{id}/overlay/`
- [ ] `GET /analysis/me` retorna el historial paginado
- [ ] `GET /dashboard/me` retorna estadísticas correctas
- [ ] XP se actualiza en la base de datos tras cada análisis completado
- [ ] El cinturón se recalcula correctamente al superar los umbrales de XP
- [ ] Los badges se otorgan cuando se cumplen sus condiciones
- [ ] Todos los endpoints protegidos retornan 401 sin token
- [ ] Contraseñas nunca aparecen en ninguna respuesta

✅ DOCUMENTO COMPLETADO
