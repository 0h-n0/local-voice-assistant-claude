"""Tests for GET /api/config endpoint."""


import pytest
from fastapi.testclient import TestClient


class TestConfigAPI:
    """Test config API endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client with mocked settings."""
        # Import here to avoid circular imports
        from src.main import app

        return TestClient(app, raise_server_exceptions=False)

    def test_get_config_returns_200(self, client: TestClient) -> None:
        """Test that GET /api/config returns 200 OK."""
        response = client.get("/api/config")
        assert response.status_code == 200

    def test_get_config_returns_json(self, client: TestClient) -> None:
        """Test that GET /api/config returns JSON."""
        response = client.get("/api/config")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_get_config_includes_tts_settings(self, client: TestClient) -> None:
        """Test that config includes TTS settings."""
        response = client.get("/api/config")
        data = response.json()
        assert "tts" in data
        assert "device" in data["tts"]
        assert "max_concurrent" in data["tts"]

    def test_get_config_includes_orchestrator_settings(
        self, client: TestClient
    ) -> None:
        """Test that config includes orchestrator settings."""
        response = client.get("/api/config")
        data = response.json()
        assert "orchestrator" in data
        assert "timeout" in data["orchestrator"]
        assert "max_concurrent" in data["orchestrator"]

    def test_get_config_includes_log_level(self, client: TestClient) -> None:
        """Test that config includes log level."""
        response = client.get("/api/config")
        data = response.json()
        assert "log_level" in data
