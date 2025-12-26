"""Integration tests for Voice Dialogue Orchestrator API."""

import io

import numpy as np
import pytest
from scipy.io import wavfile


def create_test_wav(duration: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Create a valid test WAV file."""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio)
    return buffer.getvalue()


class TestDialogueAPIIntegration:
    """Integration tests for POST /api/orchestrator/dialogue."""

    @pytest.mark.asyncio
    async def test_dialogue_full_pipeline(self, orchestrator_client):
        """Test complete voice dialogue pipeline."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        # Verify response is valid WAV
        assert response.content[:4] == b"RIFF"

    @pytest.mark.asyncio
    async def test_dialogue_with_speed_parameter(self, orchestrator_client):
        """Test dialogue with custom speed parameter."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
            data={"speed": "1.5"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dialogue_mp3_format(self, orchestrator_client):
        """Test dialogue accepts MP3 format."""
        # Note: This test uses WAV data with MP3 extension for simplicity
        # Real MP3 handling is tested at the service level
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.mp3", wav_data, "audio/mpeg")},
        )
        # Should succeed as format is checked by extension
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dialogue_returns_metadata_headers(self, orchestrator_client):
        """Test dialogue returns all expected metadata headers."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200

        # Check processing time headers
        assert float(response.headers["x-processing-time-total"]) >= 0
        assert float(response.headers["x-processing-time-stt"]) >= 0
        assert float(response.headers["x-processing-time-llm"]) >= 0
        assert float(response.headers["x-processing-time-tts"]) >= 0

        # Check input/output metadata headers
        assert float(response.headers["x-input-duration"]) >= 0
        assert int(response.headers["x-input-text-length"]) >= 0
        assert int(response.headers["x-output-text-length"]) >= 0
        assert float(response.headers["x-output-duration"]) >= 0
        assert int(response.headers["x-sample-rate"]) > 0


class TestStatusAPIIntegration:
    """Integration tests for GET /api/orchestrator/status."""

    @pytest.mark.asyncio
    async def test_status_healthy(self, orchestrator_client):
        """Test status endpoint with healthy services."""
        response = await orchestrator_client.get("/api/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "stt" in data["services"]
        assert "llm" in data["services"]
        assert "tts" in data["services"]

    @pytest.mark.asyncio
    async def test_status_response_time(self, orchestrator_client):
        """Test status endpoint responds quickly."""
        import time

        start = time.time()
        response = await orchestrator_client.get("/api/orchestrator/status")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Should respond within 500ms as per SC-004
        assert elapsed < 0.5


class TestDialogueErrorHandling:
    """Error handling tests for dialogue API."""

    @pytest.mark.asyncio
    async def test_dialogue_invalid_audio_format(self, orchestrator_client):
        """Test error response for invalid audio format."""
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.txt", b"not audio data", "text/plain")},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "INVALID_AUDIO_FORMAT"

    @pytest.mark.asyncio
    async def test_dialogue_missing_audio(self, orchestrator_client):
        """Test error response when audio file is missing."""
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            data={"speed": "1.0"},
        )
        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_dialogue_invalid_speed_too_low(self, orchestrator_client):
        """Test error response for speed below minimum."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
            data={"speed": "0.1"},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_dialogue_invalid_speed_too_high(self, orchestrator_client):
        """Test error response for speed above maximum."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
            data={"speed": "3.0"},
        )
        assert response.status_code == 422  # Validation error
