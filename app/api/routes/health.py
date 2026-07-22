"""
Health check route.

Reports application status, version, and ML model availability.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.core.constants import STATUS_HEALTHY
from app.ml.model_loader import model_manager
from app.models.response_models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health():
    """Return the current health status of the API."""
    return HealthResponse(
        status=STATUS_HEALTHY,
        version=settings.APP_VERSION,
        model_status=model_manager.status,
    )
