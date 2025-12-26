"""Pytest configuration and fixtures for backend tests."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import numpy as np
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


@pytest.fixture
def mock_tts_service():
    """Create a mock TTS service for testing."""
    from src.models.tts import TTSHealthStatus, TTSStatus
    from src.services.tts_service import TTSService

    service = TTSService.__new__(TTSService)
    service._model = MagicMock()
    service._model_loaded = True
    service._model_name = "test-model"
    service._device = "cpu"
    service._semaphore = None  # Will be set in __init__

    # Mock validate_text method
    def validate_text(text: str) -> str:
        stripped = text.strip()
        if not stripped:
            raise ValueError("Text is empty or whitespace only")
        if len(stripped) > 5000:
            raise ValueError("Text is too long (max 5000 characters)")
        return stripped

    service.validate_text = validate_text

    # Mock synthesize method
    async def mock_synthesize(text: str, speed: float = 1.0) -> tuple[int, np.ndarray]:
        service.validate_text(text)
        # Generate a short sine wave as mock audio
        sample_rate = 44100
        duration = 0.1  # 100ms
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        return sample_rate, audio

    service.synthesize = mock_synthesize

    # Mock get_status method
    def get_status() -> TTSStatus:
        return TTSStatus(
            status=TTSHealthStatus.HEALTHY,
            model_loaded=True,
            model_name="test-model",
            device="cpu",
            last_check=datetime.now(timezone.utc),
            error_message=None,
        )

    service.get_status = get_status

    return service
