"""Contract tests for Voice Dialogue Orchestrator API."""

import io

import numpy as np
import pytest
from scipy.io import wavfile


def create_test_wav() -> bytes:
    """Create a valid test WAV file."""
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio)
    return buffer.getvalue()


class TestDialogueEndpointContract:
    """Contract tests for POST /api/orchestrator/dialogue."""

    @pytest.mark.asyncio
    async def test_dialogue_returns_audio_wav(self, orchestrator_client):
        """Verify endpoint returns audio/wav content type."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

    @pytest.mark.asyncio
    async def test_dialogue_includes_processing_time_headers(self, orchestrator_client):
        """Verify endpoint includes X-Processing-Time headers."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200
        assert "x-processing-time-total" in response.headers
        assert "x-processing-time-stt" in response.headers
        assert "x-processing-time-llm" in response.headers
        assert "x-processing-time-tts" in response.headers

    @pytest.mark.asyncio
    async def test_dialogue_includes_input_output_headers(self, orchestrator_client):
        """Verify endpoint includes input/output metadata headers."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200
        assert "x-input-duration" in response.headers
        assert "x-input-text-length" in response.headers
        assert "x-output-text-length" in response.headers
        assert "x-output-duration" in response.headers
        assert "x-sample-rate" in response.headers

    @pytest.mark.asyncio
    async def test_dialogue_accepts_speed_parameter(self, orchestrator_client):
        """Verify endpoint accepts optional speed parameter."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
            data={"speed": "1.5"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_dialogue_returns_valid_wav_data(self, orchestrator_client):
        """Verify endpoint returns valid WAV audio data."""
        wav_data = create_test_wav()
        response = await orchestrator_client.post(
            "/api/orchestrator/dialogue",
            files={"audio": ("test.wav", wav_data, "audio/wav")},
        )
        assert response.status_code == 200
        # Check WAV header
        assert response.content[:4] == b"RIFF"
        assert response.content[8:12] == b"WAVE"


class TestStatusEndpointContract:
    """Contract tests for GET /api/orchestrator/status."""

    @pytest.mark.asyncio
    async def test_status_returns_json(self, orchestrator_client):
        """Verify endpoint returns JSON content type."""
        response = await orchestrator_client.get("/api/orchestrator/status")
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_status_includes_required_fields(self, orchestrator_client):
        """Verify status response includes required fields."""
        response = await orchestrator_client.get("/api/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    @pytest.mark.asyncio
    async def test_status_includes_all_services(self, orchestrator_client):
        """Verify status response includes all service statuses."""
        response = await orchestrator_client.get("/api/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        services = data["services"]
        assert "stt" in services
        assert "llm" in services
        assert "tts" in services

    @pytest.mark.asyncio
    async def test_status_service_has_required_fields(self, orchestrator_client):
        """Verify each service status has required fields."""
        response = await orchestrator_client.get("/api/orchestrator/status")
        assert response.status_code == 200
        data = response.json()
        for service_name in ["stt", "llm", "tts"]:
            service = data["services"][service_name]
            assert "status" in service
            assert "details" in service
