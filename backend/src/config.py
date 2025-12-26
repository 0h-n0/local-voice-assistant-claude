"""Configuration settings for the Local Voice Assistant Backend."""

import os
from pathlib import Path

# TTS Configuration
TTS_MODEL_PATH: Path = Path(
    os.getenv("TTS_MODEL_PATH", "model_assets/jvnv-F1-jp")
)
TTS_DEVICE: str = os.getenv("TTS_DEVICE", "cpu")
TTS_MAX_CONCURRENT: int = int(os.getenv("TTS_MAX_CONCURRENT", "3"))

# TTS Model file names (within TTS_MODEL_PATH)
TTS_MODEL_FILE: str = os.getenv("TTS_MODEL_FILE", "jvnv-F1-jp_e160_s14000.safetensors")
TTS_CONFIG_FILE: str = "config.json"
TTS_STYLE_VEC_FILE: str = "style_vectors.npy"

# BERT model for Japanese TTS
TTS_BERT_MODEL: str = "ku-nlp/deberta-v2-large-japanese-char-wwm"

# Text limits
TTS_MAX_TEXT_LENGTH: int = 5000
TTS_MIN_TEXT_LENGTH: int = 1

# Speed limits
TTS_MIN_SPEED: float = 0.5
TTS_MAX_SPEED: float = 2.0
TTS_DEFAULT_SPEED: float = 1.0

# Orchestrator Configuration
ORCHESTRATOR_MAX_CONCURRENT: int = int(os.getenv("ORCHESTRATOR_MAX_CONCURRENT", "5"))
ORCHESTRATOR_TIMEOUT: float = float(os.getenv("ORCHESTRATOR_TIMEOUT", "30"))  # seconds
ORCHESTRATOR_SEMAPHORE_TIMEOUT: float = float(
    os.getenv("ORCHESTRATOR_SEMAPHORE_TIMEOUT", "2.0")
)  # seconds to wait for semaphore
ORCHESTRATOR_MAX_AUDIO_DURATION: float = float(
    os.getenv("ORCHESTRATOR_MAX_AUDIO_DURATION", "300")
)  # 5 minutes
ORCHESTRATOR_MIN_AUDIO_DURATION: float = float(
    os.getenv("ORCHESTRATOR_MIN_AUDIO_DURATION", "0.5")
)  # 0.5 seconds

# Conversation Storage Configuration
# Default path is relative to the backend directory
_BACKEND_DIR = Path(__file__).parent.parent
_DEFAULT_DB_PATH = str(_BACKEND_DIR / "data" / "conversations.db")
CONVERSATION_DB_PATH: str = os.getenv("CONVERSATION_DB_PATH", _DEFAULT_DB_PATH)

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL: int = int(os.getenv("WS_HEARTBEAT_INTERVAL", "30"))  # seconds
WS_MAX_AUDIO_DURATION: int = int(os.getenv("WS_MAX_AUDIO_DURATION", "60"))  # seconds
WS_AUDIO_CHUNK_INTERVAL: int = int(os.getenv("WS_AUDIO_CHUNK_INTERVAL", "100"))  # ms

# Deepgram STT Configuration
DEEPGRAM_API_KEY: str = os.getenv("DEEPGRAM_API_KEY", "")
DEEPGRAM_MODEL: str = os.getenv("DEEPGRAM_MODEL", "nova-2")
DEEPGRAM_LANGUAGE: str = os.getenv("DEEPGRAM_LANGUAGE", "ja")  # Japanese
DEEPGRAM_SAMPLE_RATE: int = int(os.getenv("DEEPGRAM_SAMPLE_RATE", "16000"))
