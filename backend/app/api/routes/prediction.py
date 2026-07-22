"""
Prediction route.

Accepts feature data and returns a cholera outbreak risk prediction.
"""

from fastapi import APIRouter

from app.models.request_models import PredictionRequest
from app.models.response_models import PredictionResponse
from app.services.prediction_service import predict

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
