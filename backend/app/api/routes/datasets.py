"""
Datasets route.

Reports metadata about available model artifacts (joblib files).
"""

from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings
from app.models.response_models import DatasetInfo, DatasetsResponse

router = APIRouter(prefix="/api/v1", tags=["datasets"])


@router.get(
    "/datasets",
    response_model=DatasetsResponse,
    summary="List model artifacts",
    description="Returns metadata about the ML model and preprocessor artifacts.",
)
def list_datasets():
    """Return information about available model artifacts."""
    artifacts = [
        _artifact_info("Cholera Model", settings.abs_model_path),
        _artifact_info("Preprocessor Pipeline", settings.abs_preprocessor_path),
    ]
    return DatasetsResponse(datasets=artifacts)


def _artifact_info(name: str, path: Path) -> DatasetInfo:
    """Build a DatasetInfo for a single artifact file."""
    exists = path.exists()
    size = path.stat().st_size if exists else None
    return DatasetInfo(
        name=name,
        path=str(path),
        exists=exists,
        size_bytes=size,
    )
