"""Integration tests for TTS API endpoints.

These tests validate the full request/response flow through the API.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def tts_client(mock_tts_service):
    """Create an async test client with mocked TTS service."""
    from src.dependencies import set_tts_service
    from src.main import app

    set_tts_service(mock_tts_service)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


class TestSynthesizeEndpoint:
    """Integration tests for POST /api/tts/synthesize endpoint."""

    async def test_synthesize_simple_text_returns_wav(self, tts_client: AsyncClient):
        """Verify simple text synthesis returns valid WAV audio."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "こんにちは"},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        # WAV files start with RIFF header
        assert response.content[:4] == b"RIFF"

    async def test_synthesize_long_text_succeeds(self, tts_client: AsyncClient):
        """Verify long text (500 chars) synthesis succeeds."""
        long_text = "これはテストです。" * 50  # ~500 chars
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": long_text},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

    async def test_synthesize_empty_text_returns_error(self, tts_client: AsyncClient):
        """Verify empty text returns proper error response.

        Note: Pydantic validation catches this first, returning 422.
        """
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": ""},
        )
        # Pydantic's min_length=1 validates this before our handler
        assert response.status_code == 422

    async def test_synthesize_whitespace_only_returns_error(
        self, tts_client: AsyncClient
    ):
        """Verify whitespace-only text returns proper error response."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "   \n\t  "},
        )
        assert response.status_code == 400
        data = response.json()
        assert data["error_code"] == "EMPTY_TEXT"

    async def test_synthesize_exceeds_limit_returns_error(
        self, tts_client: AsyncClient
    ):
        """Verify text exceeding 5000 chars returns proper error.

        Note: Pydantic validation catches this first, returning 422.
        """
        too_long = "あ" * 5001
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": too_long},
        )
        # Pydantic's max_length=5000 validates this before our handler
        assert response.status_code == 422

    async def test_synthesize_missing_text_returns_422(self, tts_client: AsyncClient):
        """Verify missing text field returns validation error."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={},
        )
        assert response.status_code == 422  # FastAPI validation error


class TestSpeedParameter:
    """Integration tests for speed parameter in synthesis."""

    async def test_synthesize_with_speed_parameter(self, tts_client: AsyncClient):
        """Verify speed parameter is accepted."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "早口で話します", "speed": 1.5},
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"

    async def test_synthesize_with_slow_speed(self, tts_client: AsyncClient):
        """Verify slow speed parameter is accepted."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "ゆっくり話します", "speed": 0.7},
        )
        assert response.status_code == 200

    async def test_synthesize_without_speed_uses_default(self, tts_client: AsyncClient):
        """Verify request without speed uses default (1.0)."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "通常速度です"},
        )
        assert response.status_code == 200

    async def test_synthesize_with_invalid_speed_too_fast(
        self, tts_client: AsyncClient
    ):
        """Verify speed > 2.0 returns validation error."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "テスト", "speed": 3.0},
        )
        # Pydantic validation catches this
        assert response.status_code == 422

    async def test_synthesize_with_invalid_speed_too_slow(
        self, tts_client: AsyncClient
    ):
        """Verify speed < 0.5 returns validation error."""
        response = await tts_client.post(
            "/api/tts/synthesize",
            json={"text": "テスト", "speed": 0.1},
        )
        # Pydantic validation catches this
        assert response.status_code == 422


class TestStatusEndpoint:
    """Integration tests for GET /api/tts/status endpoint."""

    async def test_status_returns_healthy(self, tts_client: AsyncClient):
        """Verify status endpoint returns healthy status."""
        response = await tts_client.get("/api/tts/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["model_loaded"] is True
        assert "device" in data

    async def test_status_response_time_under_500ms(self, tts_client: AsyncClient):
        """Verify status endpoint responds quickly (SC-005: <500ms)."""
        import time

        start = time.time()
        response = await tts_client.get("/api/tts/status")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.5  # 500ms requirement
