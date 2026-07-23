"""
Pydantic response models.

Defines the structure of every JSON response returned by the API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ── Prediction ───────────────────────────────────────────────────────────

class ContributingFactor(BaseModel):
    """A single contributing factor with its normalised value and impact."""
    factor: str
    value: float
    impact: str


class PredictionResponse(BaseModel):
    """Full response for a cholera risk prediction."""

    location: str = Field(..., description="Location that was assessed.")
    risk_level: str = Field(..., description="Risk classification: high, moderate, or low.")
    probability: float = Field(..., ge=0, le=1, description="Outbreak probability (0–1).")
    confidence: float = Field(0.0, ge=0, le=1, description="Model confidence score.")
    model_version: str = Field("1.0.0", description="Version of the prediction model.")
    prediction_method: str = Field("rule-based", description="Method used: 'rule-based' or 'ml-model'.")
    contributing_factors: list[ContributingFactor] = Field(
        default_factory=list,
        description="Ranked list of factors contributing to the risk score.",
    )
    explanation: str = Field(..., description="Human-readable explanation of the prediction.")


# ── Health ───────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response for the /health endpoint."""
    status: str
    version: str
    model_status: str


# ── Analytics ────────────────────────────────────────────────────────────

class AnalyticsSummary(BaseModel):
    """Dashboard summary statistics."""
    total_lgas: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    average_risk_probability: float
    most_at_risk_lga: str
    data_source: str


class TrendDataPoint(BaseModel):
    """A single data point in a trend series."""
    month: int
    month_name: str
    risk_probability: float
    risk_level: str


class TrendResponse(BaseModel):
    """Historical or projected trend data."""
    location: str
    trend: list[TrendDataPoint]


class HighRiskLGA(BaseModel):
    """An LGA flagged as high risk."""
    location: str
    probability: float
    risk_level: str
    key_factors: list[str]


class HighRiskResponse(BaseModel):
    """List of high-risk LGAs."""
    count: int
    lgas: list[HighRiskLGA]


# ── Datasets ─────────────────────────────────────────────────────────────

class DatasetInfo(BaseModel):
    """Metadata about an available dataset / model artifact."""
    name: str
    path: str
    exists: bool
    size_bytes: int | None = None


class DatasetsResponse(BaseModel):
    """Available model artifacts."""
    datasets: list[DatasetInfo]


# ── Dataset Predictions ──────────────────────────────────────────────────

class DatasetRecordPrediction(BaseModel):
    """A prediction for a single row / observation in a dataset."""
    year: int | None = None
    week: int | None = None
    month: int
    location: str = Field(..., description="Local Government Area (LGA)")
    rainfall: float
    population_density: float
    wash_score: float
    risk_level: str
    probability: float
    confidence: float
    prediction_method: str
    contributing_factors: list[ContributingFactor] = Field(default_factory=list)
    explanation: str | None = None


class LGADatasetSummary(BaseModel):
    """Summary of dataset predictions for a specific Local Government Area (LGA)."""
    location: str
    total_records: int
    average_probability: float
    max_probability: float
    highest_risk_level: str
    predictions: list[DatasetRecordPrediction] = Field(default_factory=list)


class DatasetPredictionResponse(BaseModel):
    """Overall response for dataset-based predictions across Local Government Areas."""
    dataset_name: str
    total_records_processed: int
    lgas_present: list[str]
    summary_by_lga: list[LGADatasetSummary] = Field(default_factory=list)
    all_predictions: list[DatasetRecordPrediction] = Field(default_factory=list)



# ── Generic ──────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    """Standard error envelope."""
    error: str
    message: str


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    docs: str | None = None
    version: str | None = None
