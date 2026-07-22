"""
ML Model Loader.

Loads the trained scikit-learn model and preprocessing pipeline from
.joblib files at application startup.  Falls back gracefully if files
are missing so the rule-based predictor can still serve requests.
"""

from pathlib import Path
from typing import Any

import joblib

from app.core.config import settings
from app.core.logger import logger
from app.core.constants import MODEL_LOADED, MODEL_FALLBACK, MODEL_NOT_FOUND


class ModelManager:
    """Manages the lifecycle of ML model artifacts."""

    def __init__(self) -> None:
        self._model: Any | None = None
        self._preprocessor: Any | None = None
        self._status: str = MODEL_NOT_FOUND

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def model(self) -> Any | None:
        return self._model

    @property
    def preprocessor(self) -> Any | None:
        return self._preprocessor

    @property
    def status(self) -> str:
        return self._status

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    # ── Loading ──────────────────────────────────────────────────────────

    def load(self) -> None:
        """Attempt to load the real trained model artifact from disk."""
        model_path = settings.abs_model_path
        preprocessor_path = settings.abs_preprocessor_path

        self._load_artifact("model", model_path, "_model")

        if preprocessor_path != model_path and preprocessor_path.exists():
            self._load_artifact("preprocessor", preprocessor_path, "_preprocessor")

        if self._model is not None:
            self._preprocessor = self._model
            self._status = MODEL_LOADED
            logger.info("ML model loaded successfully from %s", model_path)
        else:
            self._status = MODEL_FALLBACK
            logger.warning(
                "ML model not available — falling back to rule-based predictor. "
                "Expected path: %s",
                model_path,
            )

    def _load_artifact(self, name: str, path: Path, attr: str) -> None:
        """Load a single joblib artifact, log errors gracefully."""
        if not path.exists():
            logger.warning("%s file not found at %s", name.capitalize(), path)
            return
        try:
            setattr(self, attr, joblib.load(path))
            logger.info("Loaded %s from %s", name, path)
        except Exception as exc:
            logger.error("Failed to load %s from %s: %s", name, path, exc)

    # ── Unloading ────────────────────────────────────────────────────────

    def unload(self) -> None:
        """Release model artifacts from memory."""
        self._model = None
        self._preprocessor = None
        self._status = MODEL_NOT_FOUND
        logger.info("ML model artifacts unloaded.")


# Singleton instance used throughout the application
model_manager = ModelManager()
