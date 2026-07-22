"""
Feature preprocessing utilities.

Transforms raw prediction request data into the feature vector expected
by the trained ML model.  When no trained preprocessor is available the
functions still normalise inputs for the rule-based predictor.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.core.constants import (
    MAX_DENSITY,
    MAX_POPULATION,
    MAX_RAINFALL_MM,
    PEAK_SEASON_MONTHS,
)
from app.core.logger import logger
from app.models.request_models import PredictionRequest


def build_feature_vector(request: PredictionRequest) -> dict[str, float]:
    """
    Convert a PredictionRequest into a dictionary of normalised features.

    Returns a dict rather than a raw array so downstream code stays
    readable and order-independent.
    """
    features = {
        "rainfall_norm": _clamp(request.rainfall / MAX_RAINFALL_MM),
        "wash_deficit": _clamp(1.0 - request.wash_score),
        "conflict_score": _clamp(request.conflict_score),
        "density_norm": _clamp(request.population_density / MAX_DENSITY),
        "population_norm": _clamp(request.population / MAX_POPULATION),
        "idp_camp": 1.0 if request.idp_camp else 0.0,
        "peak_season": 1.0 if request.month in PEAK_SEASON_MONTHS else 0.0,
    }

    logger.debug("Feature vector: %s", features)
    return features


def build_model_input(request: PredictionRequest) -> pd.DataFrame:
    """
    Build a pandas DataFrame matching the real sklearn pipeline input schema.

    The deployed model was trained on a richer feature set than the frontend
    payload. We derive the missing values from the available request fields so
    the current API contract can still be used without breaking compatibility.
    """
    month = int(request.month)
    rainfall = float(request.rainfall)
    population = float(request.population)
    density = float(request.population_density)
    wash_score = float(request.wash_score)
    conflict_score = float(request.conflict_score)

    safe_water_pct = _clamp(wash_score * 100.0, 0.0, 100.0)
    sanitation_pct = _clamp((1.0 - wash_score) * 100.0, 0.0, 100.0)
    washi = _clamp(wash_score * 100.0, 0.0, 100.0)
    humidity = _estimate_humidity(month, rainfall)
    temperature = _estimate_temperature(month)
    flood_risk = _estimate_flood_risk(rainfall)
    river_level = max(0.1, rainfall / 150.0)
    idp_population = population * 0.08 if request.idp_camp else population * 0.01
    health_facilities = max(1, int(population / 60000))
    previous_week_cases = max(0, int(population / 500000 * 10))
    cases_last_4_weeks = previous_week_cases * 4

    row = {
        "Year": 2026,
        "Week": 1,
        "Month": month,
        "LGA": request.location,
        "Rainfall_mm": rainfall,
        "Temperature_C": temperature,
        "Humidity_pct": humidity,
        "Flood_Risk": flood_risk,
        "River_Level_m": river_level,
        "Population_Density": density,
        "IDP_Population": idp_population,
        "Safe_Water_pct": safe_water_pct,
        "Sanitation_pct": sanitation_pct,
        "Health_Facilities": health_facilities,
        "Previous_Week_Cases": previous_week_cases,
        "Cases_Last_4_Weeks": cases_last_4_weeks,
        "Latitude": 11.5 + min(1.0, density / 100000),
        "Longitude": 13.0 + min(1.0, rainfall / 1000),
        "WASH_Index": washi,
        "Population_per_Health_Facility": max(1.0, population / max(health_facilities, 1)),
        "IDP_Ratio": idp_population / max(population, 1.0),
        "Water_Stress_Index": round(max(0.0, min(1.0, (1.0 - wash_score) * 0.6 + conflict_score * 0.4)), 6),
        "Environmental_Risk": round(max(0.0, min(1.0, rainfall / 400.0 + conflict_score * 0.25)), 6),
        "Lag_Ratio": round(max(0.0, min(1.0, previous_week_cases / max(cases_last_4_weeks, 1))), 6),
        "Rainy_Season": 1 if month in PEAK_SEASON_MONTHS or rainfall > 100 else 0,
    }
    return pd.DataFrame([row])


# ── Helpers ──────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp *value* to the [lo, hi] range."""
    return max(lo, min(value, hi))


def _estimate_humidity(month: int, rainfall: float) -> float:
    """Estimate humidity from season and rainfall."""
    base = 45.0
    if month in PEAK_SEASON_MONTHS or rainfall > 100:
        base += 20.0
    return round(_clamp(base, 0.0, 100.0), 3)


def _estimate_temperature(month: int) -> float:
    """Estimate temperature from the month."""
    seasonal = {1: 32.0, 2: 34.0, 3: 37.0, 4: 39.0, 5: 40.0, 6: 39.0, 7: 36.0, 8: 34.0, 9: 35.0, 10: 36.0, 11: 34.0, 12: 32.0}
    return seasonal.get(month, 35.0)


def _estimate_flood_risk(rainfall: float) -> float:
    """Estimate a numeric flood-risk score from rainfall."""
    if rainfall >= 180:
        return 1.0
    if rainfall >= 100:
        return 0.6
    if rainfall >= 60:
        return 0.3
    return 0.0
