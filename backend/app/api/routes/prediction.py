"""
Prediction route.

Accepts feature data and returns a cholera outbreak risk prediction.
"""

from fastapi import APIRouter, File, Query, UploadFile

from app.models.request_models import PredictionRequest
from app.models.response_models import DatasetPredictionResponse, PredictionResponse
from app.services.prediction_service import predict, predict_from_dataset

router = APIRouter(prefix="/api/v1", tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict cholera outbreak risk",
    description=(
        "Submit environmental, demographic, and conflict indicators for an LGA "
        "and receive a risk assessment with probability score and contributing factors."
    ),
)
def make_prediction(request: PredictionRequest):
    """Generate a cholera outbreak risk prediction for the given location."""
    return predict(request)


@router.get(
    "/predict/dataset",
    response_model=DatasetPredictionResponse,
    summary="Predict outbreak risk from dataset",
    description=(
        "Evaluates outbreak risk using the dataset. Returns predictions organized "
        "by Local Government Area (LGA). Supports filtering by LGA, month, and year."
    ),
)
def predict_dataset(
    location: str | None = Query(default=None, description="Filter by Local Government Area (LGA)"),
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12)"),
    year: int | None = Query(default=None, description="Filter by year"),
    limit: int = Query(default=200, ge=1, le=2000, description="Max records to process"),
):
    """Generate risk predictions across LGAs present in the server dataset."""
    return predict_from_dataset(
        location_filter=location,
        month_filter=month,
        year_filter=year,
        limit=limit,
    )


@router.get(
    "/predict/dataset/lga/{lga_name}",
    response_model=DatasetPredictionResponse,
    summary="Predict dataset outbreak risk for specific Local Government",
    description="Evaluates dataset outbreak risk for a specific Local Government Area (LGA).",
)
def predict_dataset_for_lga(
    lga_name: str,
    month: int | None = Query(default=None, ge=1, le=12, description="Filter by month (1-12)"),
    year: int | None = Query(default=None, description="Filter by year"),
    limit: int = Query(default=200, ge=1, le=2000, description="Max records to process"),
):
    """Generate risk predictions for a specific Local Government Area from the dataset."""
    return predict_from_dataset(
        location_filter=lga_name,
        month_filter=month,
        year_filter=year,
        limit=limit,
    )


@router.post(
    "/predict/dataset/upload",
    response_model=DatasetPredictionResponse,
    summary="Predict outbreak risk from uploaded CSV dataset",
    description="Upload a custom CSV dataset file to run risk predictions per Local Government Area.",
)
async def predict_uploaded_dataset(
    file: UploadFile = File(..., description="CSV dataset file"),
    location: str | None = Query(default=None, description="Filter by Local Government Area (LGA)"),
    limit: int = Query(default=200, ge=1, le=2000, description="Max records to process"),
):
    """Generate risk predictions from an uploaded CSV dataset."""
    content = await file.read()
    return predict_from_dataset(
        file_content=content,
        file_name=file.filename,
        location_filter=location,
        limit=limit,
    )

