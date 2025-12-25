"""Contract tests for WebSocket /api/stt/stream endpoint."""

import struct
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from src.dependencies import set_stt_service
from src.services.stt_service import STTService


@pytest.fixture
def mock_stt_service_for_websocket():
    """Create a mock STT service for WebSocket testing."""
    service = STTService()
    service._model = MagicMock()
    service._device = "cpu"

    # Mock transcribe_pcm to return test text
    async def mock_transcribe_pcm(pcm_data: bytes) -> str:
        return "テスト音声"

    service.transcribe_pcm = mock_transcribe_pcm
    return service


@pytest.fixture
def test_app(mock_stt_service_for_websocket):
    """Create test app with mocked STT service."""
    from src.main import app

    # Set mock service before creating TestClient
    set_stt_service(mock_stt_service_for_websocket)

    # Patch lifespan to skip model loading
    original_lifespan = app.router.lifespan_context

    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def mock_lifespan(app):
        # Skip model loading, service already set
        yield

    app.router.lifespan_context = mock_lifespan
    yield app
    app.router.lifespan_context = original_lifespan


def test_websocket_connection_accepted(test_app):
    """WebSocket connection to /api/stt/stream is accepted."""
    with (
        TestClient(test_app) as test_client,
        test_client.websocket_connect("/api/stt/stream") as websocket,
    ):
        # Connection should be accepted
        assert websocket is not None


def test_websocket_receives_partial_results(test_app):
    """WebSocket receives partial transcription results."""
    with (
        TestClient(test_app) as test_client,
        test_client.websocket_connect("/api/stt/stream") as websocket,
    ):
        # Send enough audio chunks to trigger processing (1 second = 32000 bytes)
        audio_chunk = create_audio_chunk(num_samples=16000)  # 1 second
        websocket.send_bytes(audio_chunk)

        # Should receive a message (partial or final)
        data = websocket.receive_json()
        assert "type" in data
        assert data["type"] in ["partial", "final", "error"]
        assert "text" in data


def test_websocket_handles_disconnect_gracefully(test_app):
    """WebSocket handles client disconnect gracefully."""
    with (
        TestClient(test_app) as test_client,
        test_client.websocket_connect("/api/stt/stream") as websocket,
    ):
        # Send some data (less than processing threshold)
        audio_chunk = create_audio_chunk(num_samples=1000)
        websocket.send_bytes(audio_chunk)
        # Close the connection - should not raise
        websocket.close()


def create_audio_chunk(num_samples: int = 1600) -> bytes:
    """Create an audio chunk (16kHz, 16-bit PCM)."""
    # Each sample is 2 bytes (16-bit)
    return struct.pack(f"<{num_samples}h", *([0] * num_samples))
