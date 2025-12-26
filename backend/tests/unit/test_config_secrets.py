"""Tests for SecretStr masking of API keys."""

import os
from unittest.mock import patch

from pydantic import SecretStr


class TestSecretMasking:
    """Test SecretStr masking for sensitive values."""

    def test_api_key_is_secret_str(self) -> None:
        """Test that API keys are SecretStr instances."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {"DEEPGRAM_API_KEY": "sk-test-key"}, clear=False):
            settings = Settings(_env_file=None)
            assert isinstance(settings.deepgram.api_key, SecretStr)
            assert isinstance(settings.openai.api_key, SecretStr)

        get_settings.cache_clear()

    def test_api_key_masked_in_str(self) -> None:
        """Test that API key is masked when converted to string."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        env_vars = {"DEEPGRAM_API_KEY": "sk-secret-key-12345"}
        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings(_env_file=None)
            # String representation should be masked
            str_repr = str(settings.deepgram.api_key)
            assert "sk-secret-key-12345" not in str_repr
            assert "**" in str_repr

        get_settings.cache_clear()

    def test_api_key_accessible_via_get_secret_value(self) -> None:
        """Test that API key can be accessed via get_secret_value()."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        secret_key = "sk-test-secret-key"
        with patch.dict(os.environ, {"OPENAI_API_KEY": secret_key}, clear=False):
            settings = Settings(_env_file=None)
            # Can access actual value when needed
            assert settings.openai.api_key.get_secret_value() == secret_key

        get_settings.cache_clear()

    def test_api_key_not_in_model_dump_json(self) -> None:
        """Test that API key is masked in JSON serialization."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        secret_key = "sk-super-secret"
        with patch.dict(os.environ, {"DEEPGRAM_API_KEY": secret_key}, clear=False):
            settings = Settings(_env_file=None)
            # Dump to JSON-compatible dict
            json_dict = settings.model_dump(mode="json")
            # Secret should not appear in plain text
            json_str = str(json_dict)
            assert secret_key not in json_str

        get_settings.cache_clear()

    def test_empty_api_key_is_still_secret(self) -> None:
        """Test that empty API key is still a SecretStr."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            # Empty but still SecretStr
            assert isinstance(settings.deepgram.api_key, SecretStr)
            assert settings.deepgram.api_key.get_secret_value() == ""

        get_settings.cache_clear()
