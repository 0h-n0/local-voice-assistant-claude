"""Health check API endpoint."""

from datetime import UTC, datetime

from fastapi import APIRouter

from src.models.health import HealthResponse

router = APIRouter()

# Application version
VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return the current health status of the service.

    Returns:
        HealthResponse: Current health status with version and timestamp.
    """
    return HealthResponse(
        status="healthy",
        version=VERSION,
        timestamp=datetime.now(UTC),
    )
