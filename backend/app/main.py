"""
Application entry point.

Creates the FastAPI app, registers middleware, exception handlers,
startup/shutdown events, and includes all routers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers
from app.core.logger import logger
from app.ml.model_loader import model_manager

# Ensure all ORM models are imported so Base.metadata knows about them
import app.models.database_models  # noqa: F401


# ── Lifespan (startup / shutdown) ────────────────────────────────────────

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Run startup and shutdown logic."""
    # ── Startup ──────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("  %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("  Debug mode: %s", settings.DEBUG)
    logger.info("  Docs:       http://%s:%s/docs", settings.HOST, settings.PORT)
    logger.info("=" * 60)

    # Create database tables (auto-migrate for hackathon)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created / verified.")

    # Attempt to load ML model
    model_manager.load()

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────
    model_manager.unload()
    logger.info("Application shutdown complete.")


# ── App Factory ──────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ─────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ───────────────────────────────────────────────────

register_exception_handlers(app)

# ── Routers ──────────────────────────────────────────────────────────────

app.include_router(api_router)


# ── Root endpoints ───────────────────────────────────────────────────────

@app.get("/", tags=["root"], summary="API information")
def root():
    """Return basic API information and documentation links."""
    return {
        "message": f"Welcome to the {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "predict": "/api/v1/predict",
        "analytics": "/api/v1/analytics/summary",
    }