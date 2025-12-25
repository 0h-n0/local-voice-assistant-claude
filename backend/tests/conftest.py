"""Pytest configuration and fixtures for backend tests."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    """Create an async test client for the FastAPI application."""
    from src.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
