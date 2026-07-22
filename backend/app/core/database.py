"""
Database configuration.

Sets up the SQLAlchemy engine, session factory, and declarative base.
Uses DATABASE_URL from settings — works with both SQLite (local)
and PostgreSQL (Railway) via the same interface.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# ── Engine ───────────────────────────────────────────────────────────────

# SQLite requires `check_same_thread=False` for FastAPI's threaded model.
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

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
