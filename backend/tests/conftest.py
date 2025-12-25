"""Pytest configuration and fixtures for backend tests."""

from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from src.dependencies import set_stt_service
from src.services.stt_service import STTService


@pytest.fixture
def mock_stt_service():
    """Create a mock STT service for testing."""
    service = STTService()
    # Mock the model as loaded
    service._model = MagicMock()
    service._device = "cpu"
    return service


@pytest.fixture
async def client(mock_stt_service):
    """Create an async test client for the FastAPI application."""
    from src.main import app

    # Set the mock STT service
    set_stt_service(mock_stt_service)

    # Mock transcribe to return a simple result
    async def mock_transcribe(audio_data: bytes, filename: str = "audio.wav"):
        from src.models.stt import TranscriptionResponse

        # Validate format first
        is_valid, error = mock_stt_service.validate_audio_format(filename, audio_data)
        if not is_valid:
            raise ValueError(error)

        return TranscriptionResponse(
            text="テスト音声",
            duration_seconds=1.0,
            processing_time_seconds=0.1,
            segments=None,
        )

    mock_stt_service.transcribe = mock_transcribe

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
