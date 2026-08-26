from fastapi import APIRouter, HTTPException, status

from app.model.model_loader import model_loader

router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
)
def health() -> dict[str, str]:
    """
    Liveness endpoint.

    Indicates that the application process is running.
    """

    return {
        "status": "UP",
    }


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
)
def readiness() -> dict[str, str]:
    """
    Readiness endpoint.

    Verifies that the ML model can be loaded successfully.
    """

    try:
        model_loader.get_model()

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model is not ready",
        ) from exc

    return {
        "status": "READY",
    }
