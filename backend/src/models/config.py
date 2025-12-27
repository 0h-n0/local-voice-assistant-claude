"""Configuration models using pydantic-settings.

This module provides type-safe configuration management with validation,
environment variable loading, and SecretStr masking for sensitive values.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# =============================================================================
# Sub-Settings Models
# =============================================================================


class TTSSettings(BaseSettings):
    """Text-to-Speech configuration."""

    model_config = SettingsConfigDict(env_prefix="TTS_")

    model_path: Path = Field(
        default=Path("model_assets/jvnv-F1-jp"),
        description="Path to TTS model directory",
    )
    device: str = Field(default="cpu", description="Inference device (cpu/cuda)")
    max_concurrent: int = Field(
        default=3, ge=1, description="Maximum concurrent requests"
    )
    model_file: str = Field(
        default="jvnv-F1-jp_e160_s14000.safetensors",
        description="Model file name",
    )
    config_file: str = Field(default="config.json", description="Config file name")
    style_vec_file: str = Field(
        default="style_vectors.npy", description="Style vectors file name"
    )
    bert_model: str = Field(
        default="ku-nlp/deberta-v2-large-japanese-char-wwm",
        description="BERT model for Japanese TTS",
    )
    max_text_length: int = Field(default=5000, ge=1, description="Maximum text length")
    min_text_length: int = Field(default=1, ge=1, description="Minimum text length")
    min_speed: float = Field(default=0.5, gt=0, description="Minimum playback speed")
    max_speed: float = Field(default=2.0, gt=0, description="Maximum playback speed")
    default_speed: float = Field(
        default=1.0, gt=0, description="Default playback speed"
    )


class OrchestratorSettings(BaseSettings):
    """Orchestrator configuration."""

    model_config = SettingsConfigDict(env_prefix="ORCHESTRATOR_")

    max_concurrent: int = Field(
        default=5, ge=1, description="Maximum concurrent requests"
    )
    timeout: float = Field(default=30.0, gt=0, description="Request timeout in seconds")
    semaphore_timeout: float = Field(
        default=2.0, gt=0, description="Semaphore acquisition timeout"
    )
    max_audio_duration: float = Field(
        default=300.0, gt=0, description="Maximum audio duration in seconds"
    )
    min_audio_duration: float = Field(
        default=0.5, gt=0, description="Minimum audio duration in seconds"
    )


class WebSocketSettings(BaseSettings):
    """WebSocket configuration."""

    model_config = SettingsConfigDict(env_prefix="WS_")

    heartbeat_interval: int = Field(
        default=30, ge=1, description="Ping interval in seconds"
    )
    max_audio_duration: int = Field(
        default=60, ge=1, description="Maximum audio duration in seconds"
    )
    audio_chunk_interval: int = Field(
        default=100, ge=10, description="Audio chunk interval in milliseconds"
    )


class StorageSettings(BaseSettings):
    """Storage configuration."""

    model_config = SettingsConfigDict(env_prefix="")

    conversation_db_path: str = Field(
        default="data/conversations.db",
        description="Path to conversation database",
        alias="CONVERSATION_DB_PATH",
    )


class DeepgramSettings(BaseSettings):
    """Deepgram STT configuration."""

    model_config = SettingsConfigDict(env_prefix="DEEPGRAM_", env_file=".env", extra="ignore")

    api_key: SecretStr = Field(default=SecretStr(""), description="Deepgram API Key")
    model: str = Field(default="nova-2", description="STT model name")
    language: str = Field(default="ja", description="Recognition language")
    sample_rate: int = Field(default=16000, description="Audio sample rate")


class OpenAISettings(BaseSettings):
    """OpenAI LLM configuration."""

    model_config = SettingsConfigDict(env_prefix="OPENAI_", env_file=".env", extra="ignore")

    api_key: SecretStr = Field(default=SecretStr(""), description="OpenAI API Key")
    model: str = Field(default="gpt-4o-mini", description="LLM model name")
    base_url: str = Field(default="", description="API base URL (empty for default)")
    max_tokens: int = Field(
        default=1000, ge=1, description="Maximum tokens in response"
    )
    max_concurrent: int = Field(
        default=10, ge=1, description="Maximum concurrent API requests"
    )


# =============================================================================
# Root Settings
# =============================================================================


class Settings(BaseSettings):
    """Root application settings.

    Aggregates all sub-settings and provides global configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Sub-settings (loaded from environment with their respective prefixes)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    orchestrator: OrchestratorSettings = Field(default_factory=OrchestratorSettings)
    websocket: WebSocketSettings = Field(default_factory=WebSocketSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    deepgram: DeepgramSettings = Field(default_factory=DeepgramSettings)
    openai: OpenAISettings = Field(default_factory=OpenAISettings)

    # Global settings
    log_level: str = Field(default="INFO", description="Log level")
    debug: bool = Field(default=False, description="Debug mode")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses lru_cache to ensure settings are loaded only once.

    Returns:
        Settings instance with values from environment/.env file.
    """
    return Settings()


# Global settings instance for backward compatibility
settings = get_settings()


# =============================================================================
# API Response Models
# =============================================================================


def get_safe_config() -> dict[str, object]:
    """Get configuration safe for API exposure (secrets masked).

    Returns:
        Dictionary with configuration values, API keys showing status only.
    """
    s = get_settings()

    return {
        "log_level": s.log_level,
        "debug": s.debug,
        "tts": {
            "model_path": str(s.tts.model_path),
            "device": s.tts.device,
            "max_concurrent": s.tts.max_concurrent,
            "model_file": s.tts.model_file,
            "config_file": s.tts.config_file,
            "bert_model": s.tts.bert_model,
            "max_text_length": s.tts.max_text_length,
            "default_speed": s.tts.default_speed,
        },
        "orchestrator": {
            "max_concurrent": s.orchestrator.max_concurrent,
            "timeout": s.orchestrator.timeout,
            "semaphore_timeout": s.orchestrator.semaphore_timeout,
            "max_audio_duration": s.orchestrator.max_audio_duration,
        },
        "websocket": {
            "heartbeat_interval": s.websocket.heartbeat_interval,
            "max_audio_duration": s.websocket.max_audio_duration,
            "audio_chunk_interval": s.websocket.audio_chunk_interval,
        },
        "storage": {
            "conversation_db_path": s.storage.conversation_db_path,
        },
        "openai": {
            "api_key_configured": bool(s.openai.api_key.get_secret_value()),
            "model": s.openai.model,
            "base_url": s.openai.base_url or "(default)",
            "max_tokens": s.openai.max_tokens,
            "max_concurrent": s.openai.max_concurrent,
        },
        "deepgram": {
            "api_key_configured": bool(s.deepgram.api_key.get_secret_value()),
            "model": s.deepgram.model,
            "language": s.deepgram.language,
            "sample_rate": s.deepgram.sample_rate,
        },
    }
