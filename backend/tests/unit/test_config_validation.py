"""Tests for configuration validation errors."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError


class TestConfigValidation:
    """Test configuration validation."""

    def test_invalid_max_concurrent_raises_error(self) -> None:
        """Test that invalid max_concurrent value raises validation error."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {"TTS_MAX_CONCURRENT": "0"}, clear=False):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=None)

            # Check that the error mentions the field
            error_str = str(exc_info.value)
            has_field = "max_concurrent" in error_str.lower()
            has_greater = "greater than" in error_str.lower()
            assert has_field or has_greater

        get_settings.cache_clear()

    def test_negative_timeout_raises_error(self) -> None:
        """Test that negative timeout raises validation error."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        env_vars = {"ORCHESTRATOR_TIMEOUT": "-1"}
        with patch.dict(os.environ, env_vars, clear=False), pytest.raises(
            ValidationError
        ):
            Settings(_env_file=None)

        get_settings.cache_clear()

    def test_invalid_type_raises_error(self) -> None:
        """Test that invalid type raises validation error."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        env_vars = {"TTS_MAX_CONCURRENT": "not_a_number"}
        with patch.dict(os.environ, env_vars, clear=False), pytest.raises(
            ValidationError
        ):
            Settings(_env_file=None)

        get_settings.cache_clear()

    def test_valid_values_pass_validation(self) -> None:
        """Test that valid values pass validation without error."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        valid_env = {
            "TTS_MAX_CONCURRENT": "5",
            "ORCHESTRATOR_TIMEOUT": "60",
            "WS_HEARTBEAT_INTERVAL": "45",
        }

        with patch.dict(os.environ, valid_env, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.max_concurrent == 5
            assert settings.orchestrator.timeout == 60.0
            assert settings.websocket.heartbeat_interval == 45

        get_settings.cache_clear()
