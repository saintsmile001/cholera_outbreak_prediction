"""
Feature preprocessing utilities.

Transforms raw prediction request data into the feature vector expected
by the trained ML model.  When no trained preprocessor is available the
functions still normalise inputs for the rule-based predictor.
"""

from __future__ import annotations

import numpy as np

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


def build_model_input(request: PredictionRequest) -> np.ndarray:
    """
    Build a NumPy array suitable for the trained sklearn model.

    Feature order must match what the model was trained on.
    """
    features = build_feature_vector(request)
    ordered = [
        features["rainfall_norm"],
        features["wash_deficit"],
        features["conflict_score"],
        features["density_norm"],
        features["population_norm"],
        features["idp_camp"],
        features["peak_season"],
    ]
    return np.array([ordered])


# ── Helpers ──────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp *value* to the [lo, hi] range."""
    return max(lo, min(value, hi))
