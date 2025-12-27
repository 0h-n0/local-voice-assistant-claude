"""STT Service for Japanese speech recognition using ReazonSpeech NeMo v2."""

import asyncio
import io
import logging
import time
from pathlib import Path
from typing import Any, Literal

import soundfile as sf
from pydub import AudioSegment

from src.models.stt import Segment, STTStatus, TranscriptionResponse

logger = logging.getLogger(__name__)

# Supported audio formats
SUPPORTED_FORMATS = {".wav", ".mp3", ".flac", ".ogg", ".webm", ".mp4", ".m4a"}
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100MB
TARGET_SAMPLE_RATE = 16000
BYTES_PER_SAMPLE = 2  # 16-bit audio


class AudioBuffer:
    """Buffer for accumulating audio chunks in streaming mode."""

    def __init__(self, min_samples: int = 16000) -> None:
        """Initialize audio buffer.

        Args:
            min_samples: Minimum samples before processing (default 1 second at 16kHz)
        """
        self._data = bytearray()
        self._min_samples = min_samples

    def add(self, chunk: bytes) -> None:
        """Add audio chunk to buffer."""
        self._data.extend(chunk)

    def get_data(self) -> bytes:
        """Get accumulated audio data."""
        return bytes(self._data)

    def clear(self) -> None:
        """Clear the buffer."""
        self._data.clear()

    def should_process(self) -> bool:
        """Check if buffer has enough data to process."""
        num_samples = len(self._data) // BYTES_PER_SAMPLE
        return num_samples >= self._min_samples

    def is_empty(self) -> bool:
        """Check if buffer is empty."""
        return len(self._data) == 0


class STTService:
    """Service for speech-to-text operations using ReazonSpeech NeMo v2."""

    def __init__(self) -> None:
        """Initialize STT service."""
        self._model: Any | None = None
        self._model_name = "reazonspeech-nemo-v2"
        self._device: Literal["cuda", "cpu"] = "cpu"
        self._semaphore = asyncio.Semaphore(3)  # Max 3 concurrent requests

    @property
    def model_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None

    def validate_audio_format(
        self, filename: str, data: bytes
    ) -> tuple[bool, str | None]:
        """Validate audio file format.

        Args:
            filename: Original filename with extension
            data: Raw audio file bytes

        Returns:
            Tuple of (is_valid, error_code or None)
        """
        if not data:
            return False, "EMPTY_AUDIO"

        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            return False, "UNSUPPORTED_FORMAT"

        return True, None

    async def resample_audio(self, audio_data: bytes) -> bytes:
        """Resample audio to 16kHz WAV format.

        Args:
            audio_data: Raw audio file bytes

        Returns:
            Resampled audio as 16kHz WAV bytes
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._resample_sync, audio_data)

    def _resample_sync(self, audio_data: bytes) -> bytes:
        """Synchronous audio resampling."""
        # Load audio with pydub (handles format conversion)
        audio = AudioSegment.from_file(io.BytesIO(audio_data))

        # Convert to mono if stereo
        if audio.channels > 1:
            audio = audio.set_channels(1)

        # Resample to 16kHz
        if audio.frame_rate != TARGET_SAMPLE_RATE:
            audio = audio.set_frame_rate(TARGET_SAMPLE_RATE)

        # Export as WAV
        output = io.BytesIO()
        audio.export(output, format="wav")
        return output.getvalue()

    async def load_model(self) -> None:
        """Load the ReazonSpeech NeMo model."""
        if self._model is not None:
            logger.info("Model already loaded")
            return

        logger.info("Loading ReazonSpeech NeMo model...")
        loop = asyncio.get_event_loop()

        def _load() -> Any:
            from reazonspeech.nemo.asr import load_model

            return load_model()

        try:
            self._model = await loop.run_in_executor(None, _load)
            # Check device
            import torch

            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info("Model loaded successfully on %s", self._device)
        except Exception as e:
            logger.exception("Failed to load model")
            raise RuntimeError(f"Failed to load STT model: {e}") from e

    async def transcribe(
        self,
        audio_data: bytes,
        filename: str = "audio.wav",
    ) -> TranscriptionResponse:
        """Transcribe audio data to text.

        Args:
            audio_data: Raw audio file bytes
            filename: Original filename for format detection

        Returns:
            TranscriptionResponse with transcribed text
        """
        start_time = time.time()

        # Validate format
        is_valid, error = self.validate_audio_format(filename, audio_data)
        if not is_valid:
            from src.models.stt import ErrorCode

            raise ValueError(error or ErrorCode.PROCESSING_ERROR)

        # Resample to 16kHz WAV
        wav_data = await self.resample_audio(audio_data)

        # Get audio duration
        audio_info = sf.info(io.BytesIO(wav_data))
        duration = audio_info.duration

        # Transcribe with semaphore to limit concurrent requests
        async with self._semaphore:
            result = await self._transcribe_wav(wav_data)

        processing_time = time.time() - start_time

        # Build segments if available
        segments: list[Segment] | None = None
        if hasattr(result, "segments") and result.segments:
            segments = [
                Segment(
                    text=seg.text,
                    start_time=seg.start_seconds,
                    end_time=seg.end_seconds,
                )
                for seg in result.segments
            ]

        return TranscriptionResponse(
            text=result.text,
            duration_seconds=duration,
            processing_time_seconds=processing_time,
            segments=segments,
        )

    async def _transcribe_wav(self, wav_data: bytes) -> Any:
        """Transcribe WAV data using the model.

        Args:
            wav_data: WAV audio bytes (16kHz)

        Returns:
            ReazonSpeech transcription result
        """
        if self._model is None:
            from src.models.stt import ErrorCode

            raise RuntimeError(ErrorCode.MODEL_NOT_LOADED)

        loop = asyncio.get_event_loop()

        def _transcribe() -> Any:
            from reazonspeech.nemo.asr import audio_from_numpy, transcribe

            # Read WAV data from bytes
            data, sample_rate = sf.read(io.BytesIO(wav_data))
            audio = audio_from_numpy(data, sample_rate)
            return transcribe(self._model, audio)

        return await loop.run_in_executor(None, _transcribe)

    async def transcribe_pcm(self, pcm_data: bytes) -> str:
        """Transcribe raw PCM audio data (16kHz, 16-bit, mono).

        Args:
            pcm_data: Raw PCM audio bytes

        Returns:
            Transcribed text
        """
        if self._model is None:
            from src.models.stt import ErrorCode

            raise RuntimeError(ErrorCode.MODEL_NOT_LOADED)

        # Convert PCM to WAV format

        num_samples = len(pcm_data) // 2
        sample_rate = TARGET_SAMPLE_RATE
        wav_header = self._create_wav_header(num_samples, sample_rate)
        wav_data = wav_header + pcm_data

        result = await self._transcribe_wav(wav_data)
        return str(result.text)

    def _create_wav_header(self, num_samples: int, sample_rate: int) -> bytes:
        """Create WAV file header for PCM data."""
        import struct

        num_channels = 1
        bits_per_sample = 16
        byte_rate = sample_rate * num_channels * bits_per_sample // 8
        block_align = num_channels * bits_per_sample // 8
        data_size = num_samples * block_align

        header = b"RIFF"
        header += struct.pack("<I", 36 + data_size)
        header += b"WAVE"
        header += b"fmt "
        header += struct.pack("<I", 16)
        header += struct.pack("<H", 1)
        header += struct.pack("<H", num_channels)
        header += struct.pack("<I", sample_rate)
        header += struct.pack("<I", byte_rate)
        header += struct.pack("<H", block_align)
        header += struct.pack("<H", bits_per_sample)
        header += b"data"
        header += struct.pack("<I", data_size)

        return header

    def get_status(self) -> STTStatus:
        """Get current service status."""
        memory_mb = 0.0
        if self._model is not None:
            try:
                import torch

                if torch.cuda.is_available():
                    memory_mb = torch.cuda.memory_allocated() / (1024 * 1024)
            except ImportError:
                pass

        return STTStatus(
            model_loaded=self.model_loaded,
            model_name=self._model_name,
            device=self._device,
            memory_usage_mb=memory_mb,
        )
