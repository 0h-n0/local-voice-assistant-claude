"""Configuration settings for the Local Voice Assistant Backend.

This module provides backward-compatible exports from the new pydantic-settings
based configuration system. All values are sourced from the Settings model.

Usage:
    # New style (recommended)
    from src.models.config import settings
    print(settings.tts.model_path)

    # Legacy style (backward compatible)
    from src.config import TTS_MODEL_PATH
    print(TTS_MODEL_PATH)
"""

from pathlib import Path

from src.models.config import settings

# =============================================================================
# TTS Configuration (backward compatible exports)
# =============================================================================

TTS_MODEL_PATH: Path = settings.tts.model_path
TTS_DEVICE: str = settings.tts.device
TTS_MAX_CONCURRENT: int = settings.tts.max_concurrent

# TTS Model file names (within TTS_MODEL_PATH)
TTS_MODEL_FILE: str = settings.tts.model_file
TTS_CONFIG_FILE: str = settings.tts.config_file
TTS_STYLE_VEC_FILE: str = settings.tts.style_vec_file

# BERT model for Japanese TTS
TTS_BERT_MODEL: str = settings.tts.bert_model

# Text limits
TTS_MAX_TEXT_LENGTH: int = settings.tts.max_text_length
TTS_MIN_TEXT_LENGTH: int = settings.tts.min_text_length

# Speed limits
TTS_MIN_SPEED: float = settings.tts.min_speed
TTS_MAX_SPEED: float = settings.tts.max_speed
TTS_DEFAULT_SPEED: float = settings.tts.default_speed

# =============================================================================
# Orchestrator Configuration
# =============================================================================

ORCHESTRATOR_MAX_CONCURRENT: int = settings.orchestrator.max_concurrent
ORCHESTRATOR_TIMEOUT: float = settings.orchestrator.timeout
ORCHESTRATOR_SEMAPHORE_TIMEOUT: float = settings.orchestrator.semaphore_timeout
ORCHESTRATOR_MAX_AUDIO_DURATION: float = settings.orchestrator.max_audio_duration
ORCHESTRATOR_MIN_AUDIO_DURATION: float = settings.orchestrator.min_audio_duration

# =============================================================================
# Conversation Storage Configuration
# =============================================================================

CONVERSATION_DB_PATH: str = settings.storage.conversation_db_path

# =============================================================================
# WebSocket Configuration
# =============================================================================

WS_HEARTBEAT_INTERVAL: int = settings.websocket.heartbeat_interval
WS_MAX_AUDIO_DURATION: int = settings.websocket.max_audio_duration
WS_AUDIO_CHUNK_INTERVAL: int = settings.websocket.audio_chunk_interval

# =============================================================================
# Deepgram STT Configuration
# =============================================================================

# Note: DEEPGRAM_API_KEY is a SecretStr, use .get_secret_value() when needed
DEEPGRAM_API_KEY: str = settings.deepgram.api_key.get_secret_value()
DEEPGRAM_MODEL: str = settings.deepgram.model
DEEPGRAM_LANGUAGE: str = settings.deepgram.language
DEEPGRAM_SAMPLE_RATE: int = settings.deepgram.sample_rate

# =============================================================================
# OpenAI Configuration
# =============================================================================

# Note: OPENAI_API_KEY is a SecretStr, use .get_secret_value() when needed
OPENAI_API_KEY: str = settings.openai.api_key.get_secret_value()
OPENAI_MODEL: str = settings.openai.model
OPENAI_BASE_URL: str = settings.openai.base_url
OPENAI_MAX_TOKENS: int = settings.openai.max_tokens
OPENAI_MAX_CONCURRENT: int = settings.openai.max_concurrent

# =============================================================================
# Global Settings
# =============================================================================

LOG_LEVEL: str = settings.log_level
DEBUG: bool = settings.debug
