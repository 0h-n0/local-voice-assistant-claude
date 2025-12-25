"""Health check response model."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status: Current health status of the service.
        version: Application version string.
        timestamp: Response generation timestamp in ISO 8601 format.
    """

    status: Literal["healthy", "unhealthy"]
    version: str
    timestamp: datetime
