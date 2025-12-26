"""Pytest configuration and fixtures for backend tests."""

import io
from datetime import UTC, datetime
from unittest.mock import MagicMock

import numpy as np
import pytest
from httpx import ASGITransport, AsyncClient
from scipy.io import wavfile

from src.dependencies import (
    set_llm_service,
    set_orchestrator_service,
    set_stt_service,
    set_tts_service,
)
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
            last_check=datetime.now(UTC),
            error_message=None,
        )

    service.get_status = get_status

    # Mock audio_to_wav_bytes method
    def audio_to_wav_bytes(sample_rate: int, audio: np.ndarray) -> bytes:
        buffer = io.BytesIO()
        wavfile.write(buffer, sample_rate, audio)
        return buffer.getvalue()

    service.audio_to_wav_bytes = audio_to_wav_bytes

    # Mock get_audio_length_seconds method
    def get_audio_length_seconds(sample_rate: int, audio: np.ndarray) -> float:
        return len(audio) / sample_rate

    service.get_audio_length_seconds = get_audio_length_seconds

    return service


@pytest.fixture
async def tts_client(mock_tts_service):
    """Create an async test client with mocked TTS service."""
    from src.main import app

    set_tts_service(mock_tts_service)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    from src.models.llm import LLMStatus, ServiceStatus

    # Use MagicMock for full control
    service = MagicMock()
    service._api_key = "test-key"
    service._model = "gpt-4o-mini"
    service._max_tokens = 1000
    service._last_check = None
    service._last_error = None

    # Mock api_configured property
    service.api_configured = True

    # Mock generate_response as async
    async def mock_generate_response(
        message: str, conversation_id: str
    ) -> tuple[str, None]:
        return f"これはテスト応答です。入力: {message}", None

    service.generate_response = mock_generate_response

    # Mock get_status
    def get_status() -> LLMStatus:
        return LLMStatus(
            status=ServiceStatus.HEALTHY,
            model="gpt-4o-mini",
            api_configured=True,
            active_conversations=0,
            last_check=datetime.now(UTC),
            error_message=None,
        )

    service.get_status = get_status

    return service


@pytest.fixture
def mock_stt_service_for_orchestrator():
    """Create a mock STT service optimized for orchestrator tests."""
    service = MagicMock()
    service.model_loaded = True
    service._model_name = "reazonspeech-nemo-v2"
    service._device = "cpu"

    # Mock transcribe
    async def mock_transcribe(audio_data: bytes, filename: str = "audio.wav"):
        from src.models.stt import TranscriptionResponse

        return TranscriptionResponse(
            text="テスト音声入力",
            duration_seconds=1.0,
            processing_time_seconds=0.1,
            segments=None,
        )

    service.transcribe = mock_transcribe

    # Mock get_status
    def get_status():
        from src.models.stt import STTStatus

        return STTStatus(
            model_loaded=True,
            model_name="reazonspeech-nemo-v2",
            device="cpu",
            memory_usage_mb=0.0,
        )

    service.get_status = get_status

    return service


@pytest.fixture
async def orchestrator_client(
    mock_stt_service_for_orchestrator, mock_llm_service, mock_tts_service
):
    """Create an async test client with all mocked services for orchestrator."""
    from src.main import app
    from src.services.orchestrator_service import OrchestratorService

    set_stt_service(mock_stt_service_for_orchestrator)
    set_llm_service(mock_llm_service)
    set_tts_service(mock_tts_service)

    # Create orchestrator service with mocked dependencies
    orchestrator = OrchestratorService(
        stt_service=mock_stt_service_for_orchestrator,
        llm_service=mock_llm_service,
        tts_service=mock_tts_service,
    )
    set_orchestrator_service(orchestrator)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
