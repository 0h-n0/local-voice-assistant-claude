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
ORCHESTRATOR_TIMEOUT: int = int(os.getenv("ORCHESTRATOR_TIMEOUT", "30"))
ORCHESTRATOR_MAX_AUDIO_DURATION: float = float(
    os.getenv("ORCHESTRATOR_MAX_AUDIO_DURATION", "300")
)  # 5 minutes
ORCHESTRATOR_MIN_AUDIO_DURATION: float = float(
    os.getenv("ORCHESTRATOR_MIN_AUDIO_DURATION", "0.5")
)  # 0.5 seconds
