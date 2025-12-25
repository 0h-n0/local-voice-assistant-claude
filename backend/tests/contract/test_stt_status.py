"""Contract tests for GET /api/stt/status endpoint."""

import pytest


@pytest.mark.asyncio
async def test_status_returns_model_info(client):
    """GET /api/stt/status returns model information."""
    response = await client.get("/api/stt/status")

    assert response.status_code == 200
    data = response.json()
    assert "model_loaded" in data
    assert "model_name" in data
    assert "device" in data
    assert "memory_usage_mb" in data


@pytest.mark.asyncio
async def test_status_model_loaded_is_boolean(client):
    """GET /api/stt/status returns boolean for model_loaded."""
    response = await client.get("/api/stt/status")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["model_loaded"], bool)


@pytest.mark.asyncio
async def test_status_device_is_valid(client):
    """GET /api/stt/status returns valid device value."""
    response = await client.get("/api/stt/status")

    assert response.status_code == 200
    data = response.json()
    assert data["device"] in ["cuda", "cpu"]
