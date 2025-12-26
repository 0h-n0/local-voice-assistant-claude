"""Contract tests for TTS API endpoints.

These tests validate the API contract (request/response schemas)
matches the OpenAPI spec.
"""

from httpx import AsyncClient


class TestSynthesizeContract:
    """Contract tests for POST /api/tts/synthesize endpoint."""

    async def test_synthesize_returns_wav_content_type(self, tts_client: AsyncClient):
        """Verify response has audio/wav content type."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "こんにちは"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

    async def test_synthesize_returns_processing_time_header(
        self, tts_client: AsyncClient
    ):
        """Verify response includes X-Processing-Time header."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "こんにちは"},
        )
        assert response.status_code == 200
        assert "x-processing-time" in response.headers
        processing_time = float(response.headers["x-processing-time"])
        assert processing_time >= 0

    async def test_synthesize_returns_audio_length_header(
        self, tts_client: AsyncClient
    ):
        """Verify response includes X-Audio-Length header."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "こんにちは"},
        )
        assert response.status_code == 200
        assert "x-audio-length" in response.headers
        audio_length = float(response.headers["x-audio-length"])
        assert audio_length >= 0

    async def test_synthesize_returns_sample_rate_header(self, tts_client: AsyncClient):
        """Verify response includes X-Sample-Rate header."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "こんにちは"},
        )
        assert response.status_code == 200
        assert "x-sample-rate" in response.headers
        sample_rate = int(response.headers["x-sample-rate"])
        assert sample_rate > 0

    async def test_synthesize_empty_text_returns_422(self, tts_client: AsyncClient):
        """Verify empty text returns 422 (Pydantic validation)."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": ""},
        )
        # Pydantic's min_length=1 catches this before our handler
        assert response.status_code == 422

    async def test_synthesize_text_too_long_returns_422(self, tts_client: AsyncClient):
        """Verify text exceeding limit returns 422 (Pydantic validation)."""
        long_text = "あ" * 5001  # Exceeds 5000 char limit
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": long_text},
        )
        # Pydantic's max_length=5000 catches this before our handler
        assert response.status_code == 422


class TestStatusContract:
    """Contract tests for GET /api/tts/status endpoint."""

    async def test_status_returns_required_fields(self, tts_client: AsyncClient):
        """Verify status response includes all required fields."""
        response = await tts_client.get("/api/tts/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert "device" in data
        assert "last_check" in data

    async def test_status_healthy_when_model_loaded(self, tts_client: AsyncClient):
        """Verify healthy status when model is loaded."""
        response = await tts_client.get("/api/tts/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
