from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.middleware import request_logging_middleware
from app.api.routes import health, prediction
from app.config.settings import get_settings
from app.exceptions.handlers import (
    ModelInferenceException,
    generic_exception_handler,
    model_inference_exception_handler,
    validation_exception_handler,
)
from app.logging.config import configure_logging

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    description="Production-grade ML inference API - CI-CD verified",
    version="1.0.0",
)

app.middleware("http")(request_logging_middleware)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    ModelInferenceException,
    model_inference_exception_handler,
)

app.add_exception_handler(
    Exception,
    generic_exception_handler,
)


app.include_router(health.router)
app.include_router(prediction.router)


@app.get(
    "/",
    tags=["Root"],
)
def root() -> dict[str, str]:
    """
    Root endpoint.
    """

    return {
        "service": settings.app_name,
        "environment": settings.environment,
        "status": "UP",
    }
