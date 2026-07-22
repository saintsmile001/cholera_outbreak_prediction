"""
Custom exception classes and FastAPI exception handlers.

Provides structured error responses for the API and avoids
leaking internal stack traces to clients.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.logger import logger


# ── Custom Exceptions ────────────────────────────────────────────────────

class CholeraPredictionError(Exception):
    """Base exception for the prediction system."""

    def __init__(self, message: str = "An unexpected error occurred."):
        self.message = message
        super().__init__(self.message)


class ModelNotLoadedError(CholeraPredictionError):
    """Raised when the ML model cannot be loaded or is unavailable."""

    def __init__(self, message: str = "ML model is not loaded. Using fallback predictor."):
        super().__init__(message)


class InvalidInputError(CholeraPredictionError):
    """Raised when prediction input fails domain-level validation."""

    def __init__(self, message: str = "Invalid prediction input."):
        super().__init__(message)


class DatasetError(CholeraPredictionError):
    """Raised when there is a problem loading or processing a dataset."""

    def __init__(self, message: str = "Dataset operation failed."):
        super().__init__(message)


# ── Exception Handlers ───────────────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """Attach custom exception handlers to the FastAPI application."""

    @app.exception_handler(CholeraPredictionError)
    async def cholera_error_handler(request: Request, exc: CholeraPredictionError):
        logger.error("CholeraPredictionError: %s | path=%s", exc.message, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
            },
        )

    @app.exception_handler(InvalidInputError)
    async def invalid_input_handler(request: Request, exc: InvalidInputError):
        logger.warning("InvalidInputError: %s | path=%s", exc.message, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "InvalidInputError",
                "message": exc.message,
            },
        )

    @app.exception_handler(ModelNotLoadedError)
    async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
        logger.warning("ModelNotLoadedError: %s | path=%s", exc.message, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "ModelNotLoadedError",
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )
