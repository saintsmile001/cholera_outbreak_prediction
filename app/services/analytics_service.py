"""
Analytics service — aggregates dashboard data.

Provides summary stats, trend projections, and high-risk LGA
identification.  Uses the rule-based predictor to score all Borno
LGAs with representative defaults and seasonal data.
"""

from __future__ import annotations

import calendar

from app.core.constants import BORNO_LGAS, PEAK_SEASON_MONTHS, RISK_HIGH, RISK_MODERATE
from app.core.logger import logger
from app.ml.predictor import generate_prediction
from app.models.request_models import PredictionRequest
from app.models.response_models import (
    AnalyticsSummary,
    HighRiskLGA,
    HighRiskResponse,
    TrendDataPoint,
    TrendResponse,
)


# ── Representative defaults for demo analytics ──────────────────────────
# In production these would come from a database / live data feeds.
_LGA_PROFILES: dict[str, dict] = {
    "Maiduguri":    {"rainfall": 130, "population": 800000, "density": 6500, "wash": 0.35, "conflict": 0.60, "idp": True},
    "Jere":         {"rainfall": 120, "population": 500000, "density": 5000, "wash": 0.30, "conflict": 0.65, "idp": True},
    "Konduga":      {"rainfall": 110, "population": 200000, "density": 2500, "wash": 0.25, "conflict": 0.75, "idp": True},
    "Bama":         {"rainfall": 100, "population": 120000, "density": 1800, "wash": 0.20, "conflict": 0.85, "idp": True},
    "Gwoza":        {"rainfall": 95,  "population": 150000, "density": 2200, "wash": 0.22, "conflict": 0.90, "idp": True},
    "Dikwa":        {"rainfall": 105, "population": 90000,  "density": 1600, "wash": 0.18, "conflict": 0.80, "idp": True},
    "Monguno":      {"rainfall": 100, "population": 130000, "density": 1500, "wash": 0.20, "conflict": 0.70, "idp": True},
    "Ngala":        {"rainfall": 90,  "population": 100000, "density": 1200, "wash": 0.15, "conflict": 0.85, "idp": True},
    "Damboa":       {"rainfall": 85,  "population": 80000,  "density": 1000, "wash": 0.28, "conflict": 0.72, "idp": False},
    "Mafa":         {"rainfall": 90,  "population": 60000,  "density": 900,  "wash": 0.30, "conflict": 0.55, "idp": False},
    "Kaga":         {"rainfall": 80,  "population": 55000,  "density": 700,  "wash": 0.40, "conflict": 0.40, "idp": False},
    "Gubio":        {"rainfall": 75,  "population": 50000,  "density": 600,  "wash": 0.35, "conflict": 0.50, "idp": False},
    "Magumeri":     {"rainfall": 78,  "population": 70000,  "density": 800,  "wash": 0.32, "conflict": 0.55, "idp": False},
    "Chibok":       {"rainfall": 70,  "population": 65000,  "density": 750,  "wash": 0.38, "conflict": 0.60, "idp": False},
    "Askira/Uba":   {"rainfall": 65,  "population": 70000,  "density": 650,  "wash": 0.45, "conflict": 0.35, "idp": False},
    "Biu":          {"rainfall": 55,  "population": 95000,  "density": 800,  "wash": 0.50, "conflict": 0.25, "idp": False},
    "Hawul":        {"rainfall": 50,  "population": 60000,  "density": 500,  "wash": 0.52, "conflict": 0.20, "idp": False},
    "Kwaya Kusar":  {"rainfall": 45,  "population": 40000,  "density": 400,  "wash": 0.55, "conflict": 0.15, "idp": False},
    "Bayo":         {"rainfall": 48,  "population": 45000,  "density": 450,  "wash": 0.50, "conflict": 0.18, "idp": False},
    "Shani":        {"rainfall": 42,  "population": 35000,  "density": 350,  "wash": 0.58, "conflict": 0.12, "idp": False},
    "Kukawa":       {"rainfall": 88,  "population": 55000,  "density": 500,  "wash": 0.22, "conflict": 0.65, "idp": True},
    "Mobbar":       {"rainfall": 82,  "population": 48000,  "density": 420,  "wash": 0.25, "conflict": 0.50, "idp": False},
    "Abadam":       {"rainfall": 70,  "population": 30000,  "density": 300,  "wash": 0.18, "conflict": 0.90, "idp": False},
    "Guzamala":     {"rainfall": 72,  "population": 35000,  "density": 320,  "wash": 0.20, "conflict": 0.75, "idp": False},
    "Marte":        {"rainfall": 80,  "population": 42000,  "density": 380,  "wash": 0.22, "conflict": 0.78, "idp": True},
    "Kala/Balge":   {"rainfall": 76,  "population": 28000,  "density": 280,  "wash": 0.17, "conflict": 0.82, "idp": False},
    "Nganzai":      {"rainfall": 74,  "population": 40000,  "density": 360,  "wash": 0.28, "conflict": 0.58, "idp": False},
}

# Default month for summary analytics
_DEFAULT_MONTH = 8  # August (peak season)


def _profile_for(lga: str) -> dict:
    """Get profile data for an LGA, using safe defaults for unknowns."""
    return _LGA_PROFILES.get(lga, {
        "rainfall": 60, "population": 50000, "density": 500,
        "wash": 0.40, "conflict": 0.30, "idp": False,
    })


def _make_request(lga: str, month: int) -> PredictionRequest:
    """Build a PredictionRequest from an LGA profile."""
    p = _profile_for(lga)
    return PredictionRequest(
        location=lga,
        rainfall=p["rainfall"],
        population=p["population"],
        population_density=p["density"],
        wash_score=p["wash"],
        conflict_score=p["conflict"],
        idp_camp=p["idp"],
        month=month,
    )


# ── Public API ───────────────────────────────────────────────────────────

def get_summary(month: int = _DEFAULT_MONTH) -> AnalyticsSummary:
    """Generate a dashboard summary for all Borno LGAs."""
    logger.info("Generating analytics summary for month=%d", month)

    results = []
    for lga in BORNO_LGAS:
        req = _make_request(lga, month)
        pred = generate_prediction(req)
        results.append(pred)

    high = [r for r in results if r.risk_level == RISK_HIGH]
    moderate = [r for r in results if r.risk_level == RISK_MODERATE]
    low = [r for r in results if r.risk_level not in (RISK_HIGH, RISK_MODERATE)]

    avg_prob = round(sum(r.probability for r in results) / len(results), 3) if results else 0.0
    most_at_risk = max(results, key=lambda r: r.probability).location if results else "N/A"

    return AnalyticsSummary(
        total_lgas=len(BORNO_LGAS),
        high_risk_count=len(high),
        moderate_risk_count=len(moderate),
        low_risk_count=len(low),
        average_risk_probability=avg_prob,
        most_at_risk_lga=most_at_risk,
        data_source="representative LGA profiles (demo data)",
    )


def get_trends(location: str = "Maiduguri") -> TrendResponse:
    """Return month-by-month risk trend for a given location."""
    logger.info("Generating trend data for %s", location)

    points: list[TrendDataPoint] = []
    for m in range(1, 13):
        req = _make_request(location, m)
        pred = generate_prediction(req)
        points.append(
            TrendDataPoint(
                month=m,
                month_name=calendar.month_abbr[m],
                risk_probability=pred.probability,
                risk_level=pred.risk_level,
            )
        )

    return TrendResponse(location=location, trend=points)


def get_high_risk_lgas(month: int = _DEFAULT_MONTH) -> HighRiskResponse:
    """Return all LGAs classified as high risk for a given month."""
    logger.info("Identifying high-risk LGAs for month=%d", month)

    high_risk: list[HighRiskLGA] = []
    for lga in BORNO_LGAS:
        req = _make_request(lga, month)
        pred = generate_prediction(req)
        if pred.risk_level in (RISK_HIGH, RISK_MODERATE):
            key_factors = [
                f["factor"]
                for f in pred.contributing_factors[:3]  # top 3 factors
            ] if pred.contributing_factors else []
            high_risk.append(
                HighRiskLGA(
                    location=lga,
                    probability=pred.probability,
                    risk_level=pred.risk_level,
                    key_factors=key_factors,
                )
            )

    high_risk.sort(key=lambda x: x.probability, reverse=True)
    return HighRiskResponse(count=len(high_risk), lgas=high_risk)
