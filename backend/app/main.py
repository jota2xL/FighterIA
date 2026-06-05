"""
Module: main
Description: FastAPI application entry point.
             Configures CORS, mounts static file serving for storage,
             registers all routers, creates DB tables and runs the seed on startup.
"""
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import models BEFORE create_all so SQLAlchemy Base knows all tables
import app.models  # noqa: F401 — side-effect import that registers all ORM classes

from app.config import settings
from app.database import engine, Base
from app.utils.storage import init_storage_dirs
from app.routers import auth, users, disciplines, analysis, dashboard, gamification, instructor
from app.routers import crm, blockchain, nlp

# ── Create tables ─────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── Ensure storage directories exist ─────────────────────────────────────
init_storage_dirs()

# ── FastAPI application ───────────────────────────────────────────────────
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (avatars, etc.) at /storage/*
_storage_path = pathlib.Path(settings.STORAGE_PATH)
_storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/storage", StaticFiles(directory=str(_storage_path)), name="storage")

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(disciplines.router)
app.include_router(analysis.router)
app.include_router(dashboard.router)
app.include_router(gamification.router)
app.include_router(instructor.router)
app.include_router(crm.router)
app.include_router(blockchain.router)
app.include_router(nlp.router)


# ── Startup seed ─────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event() -> None:
    """Populate disciplines, techniques, biomechanical references and badges if empty."""
    from seed.seed_data import run_seed
    run_seed()


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": settings.VERSION, "project": settings.PROJECT_NAME}
