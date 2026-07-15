"""
FinRelief AI - Application Configuration
Loads all settings from .env file using pydantic-settings.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache

# Resolve the path to the project root (where .env lives)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    # Database
    DATABASE_URL: str = "sqlite:///./finrelief.db"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Gemini AI
    GEMINI_API_KEY: str
    GEMINI_MODEL_NAME: str = "gemini-2.0-flash"

    # App
    APP_NAME: str = "FinRelief AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": str(PROJECT_ROOT / ".env"),
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
