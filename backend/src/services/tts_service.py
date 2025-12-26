"""TTS Service with Style-Bert-VITS2 integration."""

import asyncio
import io
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.io import wavfile

from src.config import (
    TTS_BERT_MODEL,
    TTS_CONFIG_FILE,
    TTS_DEFAULT_SPEED,
    TTS_DEVICE,
    TTS_MAX_CONCURRENT,
    TTS_MAX_TEXT_LENGTH,
    TTS_MODEL_FILE,
    TTS_MODEL_PATH,
    TTS_STYLE_VEC_FILE,
)
from src.models.tts import TTSHealthStatus, TTSStatus

logger = logging.getLogger(__name__)


class TTSService:
    """Text-to-Speech service using Style-Bert-VITS2."""

    def __init__(self) -> None:
        """Initialize TTS service."""
        self._model: Any = None
        self._model_loaded: bool = False
        self._model_name: str | None = None
        self._device: str = TTS_DEVICE
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(TTS_MAX_CONCURRENT)
        self._executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        self._last_error: str | None = None

    async def load_model(self) -> None:
        """Load BERT and TTS models on startup."""
        try:
            logger.info("Loading TTS models...")
            start_time = time.time()

            # Run model loading in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                self._executor, self._load_models_sync
            )

            elapsed = time.time() - start_time
            logger.info(f"TTS models loaded in {elapsed:.2f}s")
            self._model_loaded = True
            self._last_error = None
        except Exception as e:
            logger.error(f"Failed to load TTS models: {e}")
            self._model_loaded = False
            self._last_error = str(e)
            raise

    def _load_models_sync(self) -> None:
        """Synchronously load BERT and TTS models."""
        from style_bert_vits2.constants import Languages
        from style_bert_vits2.nlp import bert_models
        from style_bert_vits2.tts_model import TTSModel

        # Load BERT tokenizer and model
        logger.info(f"Loading BERT model: {TTS_BERT_MODEL}")
        bert_models.load_model(Languages.JP, TTS_BERT_MODEL)
        bert_models.load_tokenizer(Languages.JP, TTS_BERT_MODEL)

        # Load TTS model
        model_path = Path(TTS_MODEL_PATH)
        model_file = model_path / TTS_MODEL_FILE
        config_file = model_path / TTS_CONFIG_FILE
        style_vec_file = model_path / TTS_STYLE_VEC_FILE

        if not model_file.exists():
            raise FileNotFoundError(f"TTS model file not found: {model_file}")
        if not config_file.exists():
            raise FileNotFoundError(f"TTS config file not found: {config_file}")
        if not style_vec_file.exists():
            msg = f"TTS style vector file not found: {style_vec_file}"
            raise FileNotFoundError(msg)

        logger.info(f"Loading TTS model from: {model_path}")
        self._model = TTSModel(
            model_path=model_file,
            config_path=config_file,
            style_vec_path=style_vec_file,
            device=self._device,
        )
        self._model_name = model_path.name

    def validate_text(self, text: str) -> str:
        """Validate and clean input text.

        Args:
            text: Input text to validate

        Returns:
            Cleaned text

        Raises:
            ValueError: If text is empty or too long
        """
        stripped = text.strip()
        if not stripped:
            raise ValueError("Text is empty or whitespace only")
        if len(stripped) > TTS_MAX_TEXT_LENGTH:
            raise ValueError(
                f"Text is too long (max {TTS_MAX_TEXT_LENGTH} characters)"
            )
        return stripped

    async def synthesize(
        self, text: str, speed: float = TTS_DEFAULT_SPEED
    ) -> tuple[int, NDArray[np.int16]]:
        """Synthesize speech from text.

        Args:
            text: Japanese text to synthesize
            speed: Speech speed scale (0.5-2.0)

        Returns:
            Tuple of (sample_rate, audio_data)

        Raises:
            ValueError: If text is invalid
            RuntimeError: If model is not loaded or synthesis fails
        """
        # Validate text
        cleaned_text = self.validate_text(text)

        if not self._model_loaded:
            raise RuntimeError("TTS model is not loaded")

        # Acquire semaphore for concurrency control
        async with self._semaphore:
            # Convert speed to length scale (inverse relationship)
            # speed=2.0 -> length=0.5 (faster), speed=0.5 -> length=2.0 (slower)
            length_scale = 1.0 / speed

            # Run inference in executor to avoid blocking
            sr, audio = await asyncio.get_event_loop().run_in_executor(
                self._executor,
                self._synthesize_sync,
                cleaned_text,
                length_scale,
            )

            return sr, audio

    def _synthesize_sync(
        self, text: str, length_scale: float
    ) -> tuple[int, NDArray[np.int16]]:
        """Synchronously synthesize speech.

        Args:
            text: Text to synthesize
            length_scale: Length scale for speed control

        Returns:
            Tuple of (sample_rate, audio_data)
        """
        from style_bert_vits2.constants import Languages

        sr, audio = self._model.infer(
            text=text,
            language=Languages.JP,
            length=length_scale,
        )
        return sr, audio

    def audio_to_wav_bytes(
        self, sample_rate: int, audio: NDArray[np.int16]
    ) -> bytes:
        """Convert audio array to WAV bytes.

        Args:
            sample_rate: Audio sample rate
            audio: Audio data as int16 array

        Returns:
            WAV file bytes
        """
        buffer = io.BytesIO()
        wavfile.write(buffer, sample_rate, audio)
        return buffer.getvalue()

    def get_audio_length_seconds(
        self, sample_rate: int, audio: NDArray[np.int16]
    ) -> float:
        """Calculate audio length in seconds.

        Args:
            sample_rate: Audio sample rate
            audio: Audio data array

        Returns:
            Audio length in seconds
        """
        return len(audio) / sample_rate

    def get_status(self) -> TTSStatus:
        """Get service status.

        Returns:
            TTSStatus object with current service state
        """
        if self._model_loaded:
            status = TTSHealthStatus.HEALTHY
        elif self._last_error:
            status = TTSHealthStatus.UNHEALTHY
        else:
            status = TTSHealthStatus.DEGRADED

        return TTSStatus(
            status=status,
            model_loaded=self._model_loaded,
            model_name=self._model_name,
            device=self._device,
            last_check=datetime.now(UTC),
            error_message=self._last_error,
        )

    @property
    def is_ready(self) -> bool:
        """Check if service is ready to process requests."""
        return self._model_loaded
