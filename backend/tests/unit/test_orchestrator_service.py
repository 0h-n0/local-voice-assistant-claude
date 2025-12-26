"""Unit tests for OrchestratorService."""

import io
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
from scipy.io import wavfile


def create_test_wav(duration: float = 1.0, sample_rate: int = 16000) -> bytes:
    """Create a valid test WAV file."""
    t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
    audio = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    buffer = io.BytesIO()
    wavfile.write(buffer, sample_rate, audio)
    return buffer.getvalue()


class TestOrchestratorServiceValidation:
    """Tests for audio validation in OrchestratorService."""

    @pytest.mark.asyncio
    async def test_validate_audio_format_wav(self):
        """Test validation accepts WAV format."""
        from src.services.orchestrator_service import OrchestratorService

        service = OrchestratorService(
            stt_service=MagicMock(),
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )
        wav_data = create_test_wav()
        is_valid, error = service.validate_audio_format("test.wav", wav_data)
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_validate_audio_format_mp3(self):
        """Test validation accepts MP3 format."""
        from src.services.orchestrator_service import OrchestratorService

        service = OrchestratorService(
            stt_service=MagicMock(),
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )
        # Just testing format recognition, not actual MP3 content
        is_valid, error = service.validate_audio_format("test.mp3", b"fake mp3 data")
        assert is_valid is True
        assert error is None

    @pytest.mark.asyncio
    async def test_validate_audio_format_unsupported(self):
        """Test validation rejects unsupported formats."""
        from src.services.orchestrator_service import OrchestratorService

        service = OrchestratorService(
            stt_service=MagicMock(),
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )
        is_valid, error = service.validate_audio_format("test.txt", b"not audio")
        assert is_valid is False
        assert error == "INVALID_AUDIO_FORMAT"

    @pytest.mark.asyncio
    async def test_validate_audio_format_empty(self):
        """Test validation rejects empty data."""
        from src.services.orchestrator_service import OrchestratorService

        service = OrchestratorService(
            stt_service=MagicMock(),
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )
        is_valid, error = service.validate_audio_format("test.wav", b"")
        assert is_valid is False
        assert error == "INVALID_AUDIO_FORMAT"


class TestOrchestratorServicePipeline:
    """Tests for the STT→LLM→TTS pipeline."""

    @pytest.mark.asyncio
    async def test_process_dialogue_success(self):
        """Test successful dialogue processing pipeline."""
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import OrchestratorService

        # Create mocks
        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="テスト入力",
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        mock_llm = MagicMock()
        mock_llm.api_configured = True
        mock_llm.generate_response = AsyncMock(
            return_value=("テスト応答です", None)
        )

        mock_tts = MagicMock()
        mock_tts.is_ready = True
        sample_rate = 44100
        audio_data = np.zeros(sample_rate, dtype=np.int16)
        mock_tts.synthesize = AsyncMock(return_value=(sample_rate, audio_data))

        def mock_to_wav(sr, audio):
            buf = io.BytesIO()
            wavfile.write(buf, sr, audio)
            return buf.getvalue()

        mock_tts.audio_to_wav_bytes = mock_to_wav
        mock_tts.get_audio_length_seconds = lambda sr, audio: len(audio) / sr

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=mock_llm,
            tts_service=mock_tts,
        )

        wav_data = create_test_wav()
        result = await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert result is not None
        audio_bytes, metadata = result
        assert isinstance(audio_bytes, bytes)
        assert audio_bytes[:4] == b"RIFF"
        assert metadata.stt_time >= 0
        assert metadata.llm_time >= 0
        assert metadata.tts_time >= 0
        assert metadata.input_text_length == len("テスト入力")
        assert metadata.output_text_length == len("テスト応答です")

    @pytest.mark.asyncio
    async def test_process_dialogue_stt_failure(self):
        """Test pipeline handles STT failure correctly."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = False

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.STT_SERVICE_UNAVAILABLE

    @pytest.mark.asyncio
    async def test_process_dialogue_llm_failure(self):
        """Test pipeline handles LLM failure correctly."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="テスト",
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        mock_llm = MagicMock()
        mock_llm.api_configured = False

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=mock_llm,
            tts_service=MagicMock(),
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.LLM_SERVICE_UNAVAILABLE

    @pytest.mark.asyncio
    async def test_process_dialogue_tts_failure(self):
        """Test pipeline handles TTS failure correctly."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="テスト",
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        mock_llm = MagicMock()
        mock_llm.api_configured = True
        mock_llm.generate_response = AsyncMock(return_value=("応答", None))

        mock_tts = MagicMock()
        mock_tts.is_ready = False

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=mock_llm,
            tts_service=mock_tts,
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.TTS_SERVICE_UNAVAILABLE

    @pytest.mark.asyncio
    async def test_process_dialogue_empty_transcription(self):
        """Test pipeline handles empty STT result correctly."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="",  # Empty transcription
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=MagicMock(),
            tts_service=MagicMock(),
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.SPEECH_RECOGNITION_FAILED


class TestOrchestratorServiceErrorCodes:
    """Tests for specific error codes (US3)."""

    @pytest.mark.asyncio
    async def test_audio_too_short_error(self):
        """Test AUDIO_TOO_SHORT error for very short audio."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="短い",
                duration_seconds=0.3,  # Too short (< 0.5s)
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=MagicMock(api_configured=True),
            tts_service=MagicMock(is_ready=True),
        )

        wav_data = create_test_wav(duration=0.3)
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.AUDIO_TOO_SHORT
        assert exc_info.value.details is not None
        assert "duration" in exc_info.value.details

    @pytest.mark.asyncio
    async def test_audio_too_long_error(self):
        """Test AUDIO_TOO_LONG error for very long audio."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="長い音声",
                duration_seconds=400.0,  # Too long (> 300s)
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=MagicMock(api_configured=True),
            tts_service=MagicMock(is_ready=True),
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.AUDIO_TOO_LONG
        assert exc_info.value.details is not None
        assert "max_duration" in exc_info.value.details

    @pytest.mark.asyncio
    async def test_llm_rate_limited_error(self):
        """Test LLM_RATE_LIMITED error propagation."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="テスト",
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        mock_llm = MagicMock()
        mock_llm.api_configured = True
        mock_llm.generate_response = AsyncMock(
            side_effect=RuntimeError("LLM_RATE_LIMITED")
        )

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=mock_llm,
            tts_service=MagicMock(is_ready=True),
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.LLM_RATE_LIMITED
        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_synthesis_failed_error(self):
        """Test SYNTHESIS_FAILED error for TTS failure."""
        from src.models.orchestrator import OrchestratorErrorCode
        from src.models.stt import TranscriptionResponse
        from src.services.orchestrator_service import (
            OrchestratorError,
            OrchestratorService,
        )

        mock_stt = MagicMock()
        mock_stt.model_loaded = True
        mock_stt.transcribe = AsyncMock(
            return_value=TranscriptionResponse(
                text="テスト",
                duration_seconds=1.0,
                processing_time_seconds=0.1,
                segments=None,
            )
        )

        mock_llm = MagicMock()
        mock_llm.api_configured = True
        mock_llm.generate_response = AsyncMock(return_value=("応答", None))

        mock_tts = MagicMock()
        mock_tts.is_ready = True
        mock_tts.synthesize = AsyncMock(side_effect=ValueError("Invalid text"))

        service = OrchestratorService(
            stt_service=mock_stt,
            llm_service=mock_llm,
            tts_service=mock_tts,
        )

        wav_data = create_test_wav()
        with pytest.raises(OrchestratorError) as exc_info:
            await service.process_dialogue(wav_data, "test.wav", speed=1.0)

        assert exc_info.value.error_code == OrchestratorErrorCode.SYNTHESIS_FAILED
