"""
Central API router.

Aggregates all sub-routers into a single router that main.py includes.
"""

from fastapi import APIRouter

from app.api.routes.analytics import router as analytics_router
from app.api.routes.auth import router as auth_router
from app.api.routes.datasets import router as datasets_router
from app.api.routes.health import router as health_router
from app.api.routes.prediction import router as prediction_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(prediction_router)
api_router.include_router(analytics_router)
api_router.include_router(datasets_router)

