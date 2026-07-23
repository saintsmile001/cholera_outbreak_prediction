"""
Email dispatch route.

POST /api/v1/predict/send-email
Returns 202 immediately and sends the email in a background task so the
frontend never times out waiting for the Gmail SMTP handshake.
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.services.email_service import send_prediction_email

router = APIRouter(prefix="/api/v1", tags=["email"])
logger = logging.getLogger(__name__)


class LGASummaryItem(BaseModel):
    location: str
    total_records: int = 0
    average_probability: float = 0.0
    max_probability: float = 0.0
    highest_risk_level: str = "unknown"


class SendEmailRequest(BaseModel):
    recipient: str
    dataset_name: str = "Borno_Cholera_Dataset.csv"
    summary: list[LGASummaryItem] = []
    from_name: str = "CholeraGuard AI Surveillance System"


def _send_email_task(recipient: str, dataset_name: str, summary_dicts: list[dict]) -> None:
    """Background task: runs after HTTP response is already sent to client."""
    logger.info("[BG-EMAIL] Background email task started for %s", recipient)
    try:
        result = send_prediction_email(
            recipient_email=recipient,
            dataset_name=dataset_name,
            summary_by_lga=summary_dicts,
        )
        if result.get("success"):
            logger.info("[BG-EMAIL] ✓ Email delivered to %s", recipient)
        else:
            logger.error("[BG-EMAIL] ✗ Email failed: %s", result.get("message"))
    except Exception as exc:
        logger.exception("[BG-EMAIL] Unhandled SMTP error: %s", str(exc))


@router.post(
    "/predict/send-email",
    status_code=202,
    summary="Send structured prediction report email (fire-and-forget)",
    description=(
        "Accepts the email request and returns 202 immediately. "
        "Email is dispatched via Gmail SMTP in a background task."
    ),
)
def dispatch_prediction_email(
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Queue the SMTP email task and return 202 immediately — no timeout risk."""
    logger.info("[ROUTE] POST /predict/send-email — queuing background email task")
    logger.info("[ROUTE] Recipient : %s", request.recipient)
    logger.info("[ROUTE] Dataset   : %s", request.dataset_name)
    logger.info("[ROUTE] LGA count : %d", len(request.summary))

    summary_dicts = [item.model_dump() for item in request.summary]

    if not request.recipient:
        return {
            "success": False,
            "message": "Recipient email is required.",
        }

    background_tasks.add_task(
        _send_email_task,
        recipient=str(request.recipient),
        dataset_name=request.dataset_name,
        summary_dicts=summary_dicts,
    )

    logger.info("[ROUTE] Email task queued — returning 202 to client immediately")
    return {
        "success": True,
        "simulated": False,
        "message": f"Prediction report is being dispatched to {request.recipient} via choleraguard@gmail.com",
    }
