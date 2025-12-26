"""Tests for secret masking in config API response."""


import pytest
from fastapi.testclient import TestClient


class TestConfigAPISecrets:
    """Test secret masking in config API."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create test client."""
        from src.main import app

        return TestClient(app, raise_server_exceptions=False)

    def test_api_keys_not_exposed_in_config(self, client: TestClient) -> None:
        """Test that API keys are not exposed in plain text."""
        response = client.get("/api/config")
        data = response.json()

        # Check that openai and deepgram sections don't contain raw api_key
        if "openai" in data:
            openai_str = str(data["openai"])
            # API key should be masked or not present
            assert "sk-" not in openai_str or "**" in openai_str

        if "deepgram" in data:
            deepgram_str = str(data["deepgram"])
            assert "sk-" not in deepgram_str or "**" in deepgram_str

    def test_api_key_status_shown_not_value(self, client: TestClient) -> None:
        """Test that API key shows status (configured/not set) not value."""
        response = client.get("/api/config")
        data = response.json()

        # The response should indicate whether API keys are configured
        # but not expose their actual values
        response_str = str(data)

        # Should not contain patterns that look like real API keys
        # Real keys are usually 40+ characters
        import re

        # Match potential API key patterns
        potential_keys = re.findall(r'[a-zA-Z0-9]{40,}', response_str)
        # If there are any long strings, they should be masked
        for key in potential_keys:
            assert "*" in key or key.startswith("ku-nlp")  # BERT model name is ok

    def test_config_shows_api_configured_status(self, client: TestClient) -> None:
        """Test that config shows whether APIs are configured."""
        response = client.get("/api/config")
        data = response.json()

        # Response should indicate API configuration status
        # Either through a boolean or status string
        assert "openai" in data or "deepgram" in data
