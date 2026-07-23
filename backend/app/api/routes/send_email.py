"""
Email dispatch route.

POST /api/v1/predict/send-email
Sends a structured cholera outbreak prediction report email to the user.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Any

from app.services.email_service import send_prediction_email

router = APIRouter(prefix="/api/v1", tags=["email"])


class LGASummaryItem(BaseModel):
    location: str
    total_records: int = 0
    average_probability: float = 0.0
    max_probability: float = 0.0
    highest_risk_level: str = "unknown"


class SendEmailRequest(BaseModel):
    recipient: EmailStr
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
def dispatch_prediction_email(request: SendEmailRequest) -> dict[str, Any]:
    """Send a structured LGA risk prediction report to the user's email."""
    try:
        summary_dicts = [item.model_dump() for item in request.summary]
        result = send_prediction_email(
            recipient_email=request.recipient,
            dataset_name=request.dataset_name,
            summary_by_lga=summary_dicts,
        )
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message", "Email dispatch failed"))
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"SMTP email dispatch error: {str(exc)}",
        )
