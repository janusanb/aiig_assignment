"""
Application configuration settings.
Uses environment variables with sensible defaults for local development.
"""
import os
from pathlib import Path
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""

    APP_NAME: str = "AIIG Deliverables Tracker"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    API_PREFIX: str = "/api/v1"

    _DATABASE_URL_DEFAULT: str = "postgresql://postgres:postgres@localhost:5432/deliverables"

    DATABASE_URL: str = ""

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    def __init__(self):
        raw_url = os.getenv("DATABASE_URL", self._DATABASE_URL_DEFAULT)
        self.DATABASE_URL = raw_url.replace("postgres://", "postgresql://", 1) if raw_url.startswith("postgres://") else raw_url
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        extra = os.getenv("CORS_ORIGINS_EXTRA", "")
        if extra:
            self.CORS_ORIGINS = list(self.CORS_ORIGINS) + [
                o.strip() for o in extra.split(",") if o.strip()
            ]

    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set[str] = {".xlsx", ".xls", ".csv"}
    UPLOAD_DIR: Path = Path(__file__).parent.parent.parent / "data" / "uploads"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
