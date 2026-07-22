"""
Prediction service — business logic layer.

Sits between the API routes and the ML layer.  Handles request
enrichment, delegating to the predictor, and any post-processing.
"""

from app.core.logger import logger
from app.ml.predictor import generate_prediction
from app.models.request_models import PredictionRequest
from app.models.response_models import PredictionResponse


def predict(request: PredictionRequest) -> PredictionResponse:
    """
    Run a cholera outbreak risk prediction.

    This service-level function is the single entry point for
    all prediction logic.  Additional business rules (rate-limiting,
    audit logging, caching, etc.) can be added here without
    touching the route or the ML layer.
    """
    logger.info(
        "Prediction requested — location=%s, month=%d, rainfall=%.1f, idp_camp=%s",
        request.location,
        request.month,
        request.rainfall,
        request.idp_camp,
    )

    response = generate_prediction(request)

    logger.info(
        "Prediction complete — location=%s, risk=%s, prob=%.3f, method=%s",
        response.location,
        response.risk_level,
        response.probability,
        response.prediction_method,
    )

    return response
