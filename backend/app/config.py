"""
Module: config
Description: Application settings loaded from environment variables via pydantic-settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    PROJECT_NAME: str = "FighterIA"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered martial arts training platform"
    DATABASE_URL: str = "sqlite:///./fighterai.db"
    SECRET_KEY: str = "change-this-in-production-minimum-32-characters"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    STORAGE_PATH: str = "./storage"
    MAX_VIDEO_SIZE_MB: int = 200
    MAX_VIDEO_DURATION_SECONDS: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
