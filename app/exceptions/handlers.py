from datetime import UTC, datetime

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


class ModelInferenceException(Exception):
    """
    Raised when model inference fails.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle request validation failures consistently.
    """

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": exc.errors(),
            "path": request.url.path,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


async def model_inference_exception_handler(
    request: Request,
    exc: ModelInferenceException,
) -> JSONResponse:
    """
    Handle model inference failures.
    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "MODEL_INFERENCE_ERROR",
            "message": exc.message,
            "path": request.url.path,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handle unexpected application exceptions.

    Internal exception details are deliberately not returned
    to the client.
    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred",
            "path": request.url.path,
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )
