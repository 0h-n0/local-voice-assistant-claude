"""Tests for .env file loading functionality."""

import os
from pathlib import Path
from unittest.mock import patch


class TestEnvFileLoading:
    """Test .env file loading."""

    def test_settings_loads_from_env_file(self, tmp_path: Path) -> None:
        """Test that settings can load values from .env file."""
        # Create a temporary .env file
        env_file = tmp_path / ".env"
        env_file.write_text("LOG_LEVEL=DEBUG\nDEBUG=true\n")

        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # pydantic-settings reads from env file when specified
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=str(env_file))
            # Root-level settings should be loaded from env file
            assert settings.log_level == "DEBUG"
            assert settings.debug is True

        get_settings.cache_clear()

    def test_sub_settings_load_from_environment(self) -> None:
        """Test that sub-settings load from environment variables."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # Sub-settings read from environment with their prefixes
        with patch.dict(os.environ, {"TTS_DEVICE": "cuda"}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.device == "cuda"

        get_settings.cache_clear()

    def test_settings_uses_defaults_without_env_file(self) -> None:
        """Test that settings uses defaults when no .env file exists."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            # Should use defaults
            assert settings.tts.device == "cpu"
            assert settings.tts.max_concurrent == 3
            assert settings.log_level == "INFO"

        get_settings.cache_clear()

    def test_settings_handles_missing_env_file_gracefully(self) -> None:
        """Test that settings doesn't crash when .env file is missing."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            # Point to non-existent file
            settings = Settings(_env_file="/nonexistent/.env")
            # Should still work with defaults
            assert settings.tts.device == "cpu"

        get_settings.cache_clear()
