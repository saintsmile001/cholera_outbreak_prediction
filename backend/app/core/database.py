"""
Database configuration.

Sets up the SQLAlchemy engine, session factory, and declarative base.
Uses DATABASE_URL from settings — works with both SQLite (local)
and PostgreSQL (Railway) via the same interface.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings
from app.core.logger import logger


# ── Engine ───────────────────────────────────────────────────────────────

connect_args: dict[str, Any] = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False


def _build_engine() -> Any:
    """Create the SQLAlchemy engine, falling back to SQLite when needed."""
    try:
        return create_engine(
            settings.DATABASE_URL,
            connect_args=connect_args,
            echo=settings.DEBUG,
        )
    except Exception as exc:
        logger.warning("Database engine creation failed (%s); falling back to SQLite", exc)
        fallback_url = "sqlite:///./cholera.db"
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=settings.DEBUG,
        )


engine = _build_engine()

# ── Session factory ──────────────────────────────────────────────────────

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ── Declarative base ────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# ── Dependency ───────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
