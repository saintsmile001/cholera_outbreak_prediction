"""
Global constants for the Cholera Outbreak Prediction system.

Centralises magic strings, thresholds, and domain data so they are
defined once and reused throughout the project.
"""

# ── Risk Levels ──────────────────────────────────────────────────────────
RISK_HIGH = "high"
RISK_MODERATE = "moderate"
RISK_LOW = "low"

RISK_LABELS = {
    RISK_HIGH: "High Risk",
    RISK_MODERATE: "Moderate Risk",
    RISK_LOW: "Low Risk",
}

# ── Feature Weights (rule-based predictor) ───────────────────────────────
WEIGHT_RAINFALL = 0.25
WEIGHT_WASH = 0.20
WEIGHT_CONFLICT = 0.15
WEIGHT_IDP_CAMP = 0.15
WEIGHT_DENSITY = 0.10
WEIGHT_POPULATION = 0.10
WEIGHT_SEASON = 0.05

# ── Normalisation Caps ───────────────────────────────────────────────────
MAX_RAINFALL_MM = 120.0
MAX_POPULATION = 500_000
MAX_DENSITY = 10_000.0

# ── Seasonal Risk Months (peak rainy season in Borno) ────────────────────
PEAK_SEASON_MONTHS = {7, 8, 9, 10}

# ── Borno State Local Government Areas ───────────────────────────────────
BORNO_LGAS: list[str] = [
    "Abadam",
    "Askira/Uba",
    "Bama",
    "Bayo",
    "Biu",
    "Chibok",
    "Damboa",
    "Dikwa",
    "Gubio",
    "Guzamala",
    "Gwoza",
    "Hawul",
    "Jere",
    "Kaga",
    "Kala/Balge",
    "Konduga",
    "Kukawa",
    "Kwaya Kusar",
    "Mafa",
    "Magumeri",
    "Maiduguri",
    "Marte",
    "Mobbar",
    "Monguno",
    "Ngala",
    "Nganzai",
    "Shani",
]

# ── Status Messages ──────────────────────────────────────────────────────
STATUS_HEALTHY = "healthy"
STATUS_DEGRADED = "degraded"
STATUS_UNHEALTHY = "unhealthy"

# ── Model Status ─────────────────────────────────────────────────────────
MODEL_LOADED = "loaded"
MODEL_FALLBACK = "rule-based fallback"
MODEL_NOT_FOUND = "model file not found"
