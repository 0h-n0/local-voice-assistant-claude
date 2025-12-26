"""Tests for path validation in configuration."""

import os
from pathlib import Path
from unittest.mock import patch


class TestPathValidation:
    """Test path validation in configuration."""

    def test_model_path_allows_nonexistent_path(self) -> None:
        """Test that nonexistent model path doesn't raise on config load.

        Validation of path existence should happen at startup, not during
        config loading, to allow for cleaner error messages.
        """
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        # Non-existent path should not raise during Settings creation
        with patch.dict(
            os.environ, {"TTS_MODEL_PATH": "/nonexistent/path"}, clear=False
        ):
            settings = Settings(_env_file=None)
            # Path is set but doesn't exist
            assert settings.tts.model_path == Path("/nonexistent/path")
            assert not settings.tts.model_path.exists()

        get_settings.cache_clear()

    def test_model_path_accepts_relative_path(self) -> None:
        """Test that relative paths are accepted."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(
            os.environ, {"TTS_MODEL_PATH": "relative/model/path"}, clear=False
        ):
            settings = Settings(_env_file=None)
            assert settings.tts.model_path == Path("relative/model/path")

        get_settings.cache_clear()

    def test_model_path_accepts_absolute_path(self, tmp_path: Path) -> None:
        """Test that absolute paths are accepted."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        abs_path = str(tmp_path / "models" / "tts")

        with patch.dict(os.environ, {"TTS_MODEL_PATH": abs_path}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.model_path == Path(abs_path)
            assert settings.tts.model_path.is_absolute()

        get_settings.cache_clear()

    def test_conversation_db_path_configurable(self, tmp_path: Path) -> None:
        """Test that conversation database path is configurable."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        custom_db = str(tmp_path / "custom.db")

        with patch.dict(
            os.environ, {"CONVERSATION_DB_PATH": custom_db}, clear=False
        ):
            settings = Settings(_env_file=None)
            assert settings.storage.conversation_db_path == custom_db

        get_settings.cache_clear()
