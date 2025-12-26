"""Tests for URL configuration."""

import os
from unittest.mock import patch


class TestURLConfig:
    """Test URL configuration."""

    def test_openai_base_url_default_empty(self) -> None:
        """Test that OpenAI base URL defaults to empty string."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            # Default is empty string (uses OpenAI default endpoint)
            assert settings.openai.base_url == ""

        get_settings.cache_clear()

    def test_openai_base_url_configurable(self) -> None:
        """Test that OpenAI base URL can be configured."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        custom_url = "https://custom-openai.example.com/v1"

        with patch.dict(os.environ, {"OPENAI_BASE_URL": custom_url}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == custom_url

        get_settings.cache_clear()

    def test_openai_base_url_for_azure(self) -> None:
        """Test that OpenAI base URL works for Azure OpenAI."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # Azure OpenAI example
        azure_url = "https://mycompany.openai.azure.com/openai/deployments/gpt-4"

        with patch.dict(os.environ, {"OPENAI_BASE_URL": azure_url}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == azure_url

        get_settings.cache_clear()

    def test_openai_base_url_for_local_llm(self) -> None:
        """Test that OpenAI base URL works for local LLM servers."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # Local LLM server (e.g., Ollama, LM Studio)
        local_url = "http://localhost:11434/v1"

        with patch.dict(os.environ, {"OPENAI_BASE_URL": local_url}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.openai.base_url == local_url

        get_settings.cache_clear()
