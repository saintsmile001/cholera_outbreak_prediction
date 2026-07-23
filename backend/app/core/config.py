"""
Centralized application configuration.

Loads settings from environment variables and .env file using Pydantic Settings.
All configuration values are typed and validated at startup.
"""

from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the backend directory (two levels up from this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "AI-Powered Cholera Outbreak Prediction API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "Backend API for predicting cholera outbreak risk in Borno State, Nigeria. "
        "Uses environmental, demographic, and conflict indicators to estimate outbreak probability."
    )
    DEBUG: bool = True

    # ── Server ───────────────────────────────────────────────────────────
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ── API ──────────────────────────────────────────────────────────────
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:5173",
        "https://cholera-prediction.vercel.app",
    ]
    CORS_ORIGIN_REGEX: str | None = None

    # ── ML Model Paths ───────────────────────────────────────────────────
    MODEL_PATH: str = "realdata/cholera_outbreak_model.pkl"
    PREPROCESSOR_PATH: str = "realdata/cholera_outbreak_model.pkl"

    # ── Risk Thresholds ──────────────────────────────────────────────────
    HIGH_RISK_THRESHOLD: float = 0.7
    MODERATE_RISK_THRESHOLD: float = 0.4

    # ── Database ─────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./cholera.db"

    # ── JWT / Authentication ─────────────────────────────────────────────
    JWT_SECRET_KEY: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_RESET_TOKEN_EXPIRE_MINUTES: int = 15

    # ── SMTP / Email ─────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = "choleraguard@gmail.com"
    SMTP_PASSWORD: str = ""
    SENDER_EMAIL: str = "choleraguard@gmail.com"
    SENDER_NAME: str = "CholeraGuard AI Surveillance System"

    @property
    def abs_model_path(self) -> Path:
        """Return the absolute path to the trained model file."""
        return BASE_DIR / self.MODEL_PATH

    @property
    def abs_preprocessor_path(self) -> Path:
        """Return the absolute path to the preprocessing pipeline file."""
        return BASE_DIR / self.PREPROCESSOR_PATH


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()


# Convenience alias used throughout the application
settings = get_settings()
