"""
Analytics routes.

Provides dashboard summary, historical trends, and high-risk LGA data.
"""

from fastapi import APIRouter, Query

from app.core.constants import BORNO_LGAS
from app.models.response_models import (
    AnalyticsSummary,
    HighRiskResponse,
    TrendResponse,
)
from app.services.analytics_service import (
    get_high_risk_lgas,
    get_summary,
    get_trends,
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Dashboard summary",
    description="Returns aggregate risk statistics across all 27 Borno LGAs.",
)
def analytics_summary(
    month: int = Query(default=8, ge=1, le=12, description="Month to analyse (1-12)."),
):
    """Return risk summary across all Borno LGAs for a given month."""
    return get_summary(month)


@router.get(
    "/trends",
    response_model=TrendResponse,
    summary="Monthly risk trends",
    description="Returns month-by-month risk probability for a specific location.",
)
def analytics_trends(
    location: str = Query(
        default="Maiduguri",
        description="LGA name to generate trend for.",
    ),
):
    """Return 12-month risk trend for a location."""
    return get_trends(location)


@router.get(
    "/high-risk",
    response_model=HighRiskResponse,
    summary="High-risk LGAs",
    description="Returns all LGAs classified as high or moderate risk.",
)
def analytics_high_risk(
    month: int = Query(default=8, ge=1, le=12, description="Month to analyse (1-12)."),
):
    """Return LGAs with high or moderate outbreak risk."""
    return get_high_risk_lgas(month)


@router.get(
    "/lgas",
    summary="List all LGAs",
    description="Returns the complete list of Borno State Local Government Areas.",
)
def list_lgas():
    """Return all 27 Borno LGAs."""
    return {"count": len(BORNO_LGAS), "lgas": BORNO_LGAS}
