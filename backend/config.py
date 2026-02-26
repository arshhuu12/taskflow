"""
config.py
---------
Application configuration using Pydantic BaseSettings.
Values are read from environment variables or a .env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────────────
    APP_NAME: str = "TaskFlow API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"          # "development" | "production"
    DEBUG: bool = True

    # ── Database ──────────────────────────────────────────────────────────────
    # SQLite for local dev.
    # For Render (PostgreSQL), set DATABASE_URL as an env var, e.g.:
    #   DATABASE_URL=postgresql://user:password@host:5432/taskflow_db
    DATABASE_URL: str = "postgresql://taskflow_db_k4so_user:63c7ew8rWnDopsBiQsXm7EclQyuQSqdT@dpg-d6g1j7cr85hc73aolqs0-a/taskflow_db_k4so"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # In production, replace with your frontend origin(s).
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "https://taskflow-frontend-22la.onrender.com"
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings singleton (avoids re-reading .env on every call)."""
    return Settings()


# Convenience import – other modules do:  from config import settings
settings: Settings = get_settings()
