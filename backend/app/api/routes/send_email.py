"""
Email dispatch route.

POST /api/v1/predict/send-email
Sends a structured cholera outbreak prediction report email to the user.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.email_service import send_prediction_email

router = APIRouter(prefix="/api/v1", tags=["email"])
_executor = ThreadPoolExecutor(max_workers=4)
logger = logging.getLogger(__name__)


class LGASummaryItem(BaseModel):
    location: str
    total_records: int = 0
    average_probability: float = 0.0
    max_probability: float = 0.0
    highest_risk_level: str = "unknown"


class SendEmailRequest(BaseModel):
    recipient: str  # plain str avoids strict EmailStr validation issues on Railway
    dataset_name: str = "Borno_Cholera_Dataset.csv"
    summary: list[LGASummaryItem] = []
    from_name: str = "CholeraGuard AI Surveillance System"


@router.post(
    "/predict/send-email",
    summary="Send structured prediction report email",
    description=(
        "Dispatches a structured cholera outbreak risk prediction report email "
        "to the specified recipient email address via Gmail SMTP."
    ),
)
async def dispatch_prediction_email(request: SendEmailRequest) -> dict[str, Any]:
    """Send a structured LGA risk prediction report to the user's email (non-blocking)."""
    logger.info("[ROUTE] POST /predict/send-email received")
    logger.info("[ROUTE] Recipient  : %s", request.recipient)
    logger.info("[ROUTE] Dataset    : %s", request.dataset_name)
    logger.info("[ROUTE] LGA count  : %d", len(request.summary))
    logger.info("[ROUTE] LGAs       : %s", [s.location for s in request.summary])

    try:
        summary_dicts = [item.model_dump() for item in request.summary]
        logger.info("[ROUTE] Submitting SMTP task to thread executor...")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor,
            lambda: send_prediction_email(
                recipient_email=str(request.recipient),
                dataset_name=request.dataset_name,
                summary_by_lga=summary_dicts,
            ),
        )

        logger.info("[ROUTE] Email service returned: %s", result)

        if not result.get("success"):
            logger.error("[ROUTE] Email dispatch reported failure: %s", result.get("message"))
            raise HTTPException(
                status_code=500,
                detail=result.get("message", "Email dispatch failed"),
            )
        return result

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("[ROUTE] Unhandled exception during email dispatch: %s", str(exc))
        raise HTTPException(
            status_code=500,
            detail=f"SMTP email dispatch error: {str(exc)}",
        )
