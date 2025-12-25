"""Health check API endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter

from src import __version__
from src.models.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return the current health status of the service.

    Returns:
        HealthResponse: Current health status with version and timestamp.
    """
    return HealthResponse(
        status="healthy",
        version=__version__,
        timestamp=datetime.now(UTC),
    )
