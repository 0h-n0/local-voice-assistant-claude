"""Configuration API endpoints."""

from typing import Any

from fastapi import APIRouter

from src.models.config import get_safe_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
async def get_config() -> dict[str, Any]:
    """Get current application configuration.

    Returns configuration values with sensitive information masked.
    API keys show configured status (true/false) instead of actual values.

    Returns:
        Dictionary containing current configuration.

    Note:
        For production, consider adding authentication or rate limiting
        to this endpoint.
    """
    return get_safe_config()
