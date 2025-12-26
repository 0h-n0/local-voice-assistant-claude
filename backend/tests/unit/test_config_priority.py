"""Tests for environment variable priority over .env file."""

import os
from pathlib import Path
from unittest.mock import patch


class TestEnvVariablePriority:
    """Test that environment variables take priority over .env file."""

    def test_env_variable_overrides_env_file(self, tmp_path: Path) -> None:
        """Test that environment variables override .env file values."""
        # Create a temporary .env file with one value
        env_file = tmp_path / ".env"
        env_file.write_text("TTS_DEVICE=cuda\n")

        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # Set environment variable to different value
        with patch.dict(os.environ, {"TTS_DEVICE": "cpu"}, clear=False):
            original_cwd = os.getcwd()
            os.chdir(tmp_path)
            try:
                settings = Settings(_env_file=str(env_file))
                # Environment variable should win
                assert settings.tts.device == "cpu"
            finally:
                os.chdir(original_cwd)
                get_settings.cache_clear()

    def test_env_variable_overrides_default(self) -> None:
        """Test that environment variables override default values."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {"TTS_MAX_CONCURRENT": "10"}, clear=False):
            settings = Settings(_env_file=None)
            # Environment variable should override default (3)
            assert settings.tts.max_concurrent == 10

        get_settings.cache_clear()

    def test_multiple_env_variables_override(self) -> None:
        """Test that multiple environment variables all override correctly."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        env_vars = {
            "TTS_DEVICE": "cuda",
            "ORCHESTRATOR_TIMEOUT": "60",
            "LOG_LEVEL": "DEBUG",
        }

        with patch.dict(os.environ, env_vars, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.device == "cuda"
            assert settings.orchestrator.timeout == 60.0
            assert settings.log_level == "DEBUG"

        get_settings.cache_clear()
