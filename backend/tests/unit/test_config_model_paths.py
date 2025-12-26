"""Tests for model path configuration."""

import os
from pathlib import Path
from unittest.mock import patch


class TestModelPathConfig:
    """Test model path configuration."""

    def test_tts_model_path_default(self) -> None:
        """Test that TTS model path has sensible default."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            assert settings.tts.model_path == Path("model_assets/jvnv-F1-jp")

        get_settings.cache_clear()

    def test_tts_model_path_configurable(self, tmp_path: Path) -> None:
        """Test that TTS model path can be configured via environment."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        custom_path = str(tmp_path / "custom_model")

        with patch.dict(os.environ, {"TTS_MODEL_PATH": custom_path}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.model_path == Path(custom_path)

        get_settings.cache_clear()

    def test_tts_model_file_configurable(self) -> None:
        """Test that TTS model file name can be configured."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        custom_file = "custom_model.safetensors"

        with patch.dict(os.environ, {"TTS_MODEL_FILE": custom_file}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.model_file == custom_file

        get_settings.cache_clear()

    def test_tts_config_file_configurable(self) -> None:
        """Test that TTS config file name can be configured."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        custom_config = "custom_config.json"

        with patch.dict(os.environ, {"TTS_CONFIG_FILE": custom_config}, clear=False):
            settings = Settings(_env_file=None)
            assert settings.tts.config_file == custom_config

        get_settings.cache_clear()

    def test_model_path_is_path_type(self) -> None:
        """Test that model path is a Path object, not a string."""
        from src.models.config import Settings, get_settings

        get_settings.cache_clear()

        with patch.dict(os.environ, {}, clear=True):
            settings = Settings(_env_file=None)
            assert isinstance(settings.tts.model_path, Path)

        get_settings.cache_clear()
