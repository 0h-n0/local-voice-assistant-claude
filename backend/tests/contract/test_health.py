"""Contract tests for the /health endpoint."""

from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client: AsyncClient) -> None:
    """Test that /health endpoint returns 200 OK."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_returns_correct_schema(client: AsyncClient) -> None:
    """Test that /health endpoint returns correct response schema."""
    response = await client.get("/health")
    data = response.json()

    # Check required fields exist
    assert "status" in data
    assert "version" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_endpoint_status_is_healthy(client: AsyncClient) -> None:
    """Test that /health endpoint returns healthy status."""
    response = await client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_endpoint_version_is_string(client: AsyncClient) -> None:
    """Test that /health endpoint returns version as string."""
    response = await client.get("/health")
    data = response.json()

    assert isinstance(data["version"], str)
    assert len(data["version"]) > 0


@pytest.mark.asyncio
async def test_health_endpoint_timestamp_is_valid_iso8601(client: AsyncClient) -> None:
    """Test that /health endpoint returns valid ISO 8601 timestamp."""
    response = await client.get("/health")
    data = response.json()

    # Should not raise exception if valid ISO 8601
    timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
    assert timestamp is not None
