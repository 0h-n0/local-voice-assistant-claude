"""Configuration API Contract.

This file defines the API contract for the configuration management feature.
It serves as a reference for implementation and testing.
"""

from pydantic import BaseModel, Field, SecretStr
from pathlib import Path


# =============================================================================
# Settings Models (pydantic-settings based)
# =============================================================================


class TTSSettings(BaseModel):
    """TTS (Text-to-Speech) configuration."""

    model_path: Path = Field(
        default=Path("model_assets/jvnv-F1-jp"),
        description="Path to TTS model directory",
    )
    device: str = Field(default="cpu", description="Inference device (cpu/cuda)")
    max_concurrent: int = Field(default=3, ge=1, description="Maximum concurrent requests")
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
    default_speed: float = Field(default=1.0, gt=0, description="Default playback speed")


class OrchestratorSettings(BaseModel):
    """Orchestrator configuration."""

    max_concurrent: int = Field(default=5, ge=1, description="Maximum concurrent requests")
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


class DeepgramSettings(BaseModel):
    """Deepgram STT configuration."""

    api_key: SecretStr = Field(default=SecretStr(""), description="Deepgram API Key")
    model: str = Field(default="nova-2", description="STT model name")
    language: str = Field(default="ja", description="Recognition language")
    sample_rate: int = Field(default=16000, description="Audio sample rate")


class WebSocketSettings(BaseModel):
    """WebSocket configuration."""

    heartbeat_interval: int = Field(default=30, ge=1, description="Ping interval in seconds")
    max_audio_duration: int = Field(
        default=60, ge=1, description="Maximum audio duration in seconds"
    )
    audio_chunk_interval: int = Field(
        default=100, ge=10, description="Audio chunk interval in milliseconds"
    )


class StorageSettings(BaseModel):
    """Storage configuration."""

    conversation_db_path: str = Field(
        default="data/conversations.db", description="Path to conversation database"
    )


class OpenAISettings(BaseModel):
    """OpenAI LLM configuration."""

    api_key: SecretStr = Field(default=SecretStr(""), description="OpenAI API Key")
    model: str = Field(default="gpt-4", description="LLM model name")
    base_url: str = Field(
        default="https://api.openai.com/v1", description="API base URL"
    )


# =============================================================================
# API Response Models
# =============================================================================


class ConfigInfoResponse(BaseModel):
    """Response model for GET /api/config endpoint.

    All secret values are automatically masked by Pydantic's SecretStr.
    """

    tts: dict = Field(description="TTS configuration")
    orchestrator: dict = Field(description="Orchestrator configuration")
    deepgram: dict = Field(description="Deepgram configuration (api_key masked)")
    websocket: dict = Field(description="WebSocket configuration")
    storage: dict = Field(description="Storage configuration")
    openai: dict = Field(description="OpenAI configuration (api_key masked)")
    log_level: str = Field(description="Current log level")
    debug: bool = Field(description="Debug mode status")

    model_config = {"json_schema_extra": {"example": {
        "tts": {
            "model_path": "model_assets/jvnv-F1-jp",
            "device": "cpu",
            "max_concurrent": 3,
        },
        "orchestrator": {
            "max_concurrent": 5,
            "timeout": 30.0,
        },
        "deepgram": {
            "api_key": "**********",
            "model": "nova-2",
            "language": "ja",
        },
        "websocket": {
            "heartbeat_interval": 30,
            "max_audio_duration": 60,
        },
        "storage": {
            "conversation_db_path": "data/conversations.db",
        },
        "openai": {
            "api_key": "**********",
            "model": "gpt-4",
        },
        "log_level": "INFO",
        "debug": False,
    }}}


# =============================================================================
# API Endpoints
# =============================================================================

# GET /api/config
#
# Description: Get current configuration with masked secrets
#
# Response: 200 OK
#   Body: ConfigInfoResponse
#
# Notes:
#   - All SecretStr values are automatically masked as "**********"
#   - This endpoint is for debugging purposes
#   - Consider restricting access in production
