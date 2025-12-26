"""Tests for URL validation in configuration."""

import os
from unittest.mock import patch


class TestURLValidation:
    """Test URL validation in configuration."""

    def test_empty_base_url_is_valid(self) -> None:
        """Test that empty base URL is valid (uses default endpoint)."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {"OPENAI_BASE_URL": ""}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == ""

        get_settings.cache_clear()

    def test_http_url_is_valid(self) -> None:
        """Test that HTTP URLs are valid (for local development)."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(
            os.environ, {"OPENAI_BASE_URL": "http://localhost:8080"}, clear=False
        ):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == "http://localhost:8080"

        get_settings.cache_clear()

    def test_https_url_is_valid(self) -> None:
        """Test that HTTPS URLs are valid."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(
            os.environ, {"OPENAI_BASE_URL": "https://api.example.com/v1"}, clear=False
        ):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == "https://api.example.com/v1"

        get_settings.cache_clear()

    def test_url_with_path_is_valid(self) -> None:
        """Test that URLs with paths are valid."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        url_with_path = "https://api.example.com/openai/v1/chat"

        with patch.dict(os.environ, {"OPENAI_BASE_URL": url_with_path}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == url_with_path

        get_settings.cache_clear()

    def test_url_with_port_is_valid(self) -> None:
        """Test that URLs with ports are valid."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(
            os.environ, {"OPENAI_BASE_URL": "https://api.example.com:8443/v1"},
            clear=False,
        ):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == "https://api.example.com:8443/v1"

        get_settings.cache_clear()
