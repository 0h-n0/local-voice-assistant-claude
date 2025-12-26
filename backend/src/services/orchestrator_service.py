"""Voice Dialogue Orchestrator Service.

Integrates STT → LLM → TTS pipeline for single-turn voice dialogue.
"""

import asyncio
import logging
import time
import uuid
from pathlib import Path

from src.config import (
    ORCHESTRATOR_MAX_AUDIO_DURATION,
    ORCHESTRATOR_MAX_CONCURRENT,
    ORCHESTRATOR_MIN_AUDIO_DURATION,
)
from src.models.orchestrator import (
    HealthStatus,
    OrchestratorErrorCode,
    OrchestratorStatus,
    ProcessingMetadata,
    ServiceStatus,
)
from src.services.llm_service import LLMService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService

logger = logging.getLogger(__name__)

# Supported audio formats for orchestrator (extended from STT)
SUPPORTED_FORMATS = {".wav", ".mp3", ".m4a", ".webm", ".flac", ".ogg"}


class OrchestratorError(Exception):
    """Exception raised by orchestrator service."""

    def __init__(
        self,
        error_code: OrchestratorErrorCode,
        message: str,
        details: dict[str, object] | None = None,
        retry_after: int | None = None,
    ) -> None:
        """Initialize orchestrator exception.

        Args:
            error_code: Error code enum value
            message: Human-readable error message
            details: Optional additional error details
            retry_after: Optional retry delay in seconds
        """
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.details = details
        self.retry_after = retry_after


class OrchestratorService:
    """Service for voice dialogue orchestration.

    Coordinates STT, LLM, and TTS services to process voice input
    and generate voice output in a single pipeline.
    """

    def __init__(
        self,
        stt_service: STTService,
        llm_service: LLMService,
        tts_service: TTSService,
    ) -> None:
        """Initialize orchestrator service.

        Args:
            stt_service: Speech-to-text service
            llm_service: Language model service
            tts_service: Text-to-speech service
        """
        self._stt = stt_service
        self._llm = llm_service
        self._tts = tts_service
        self._semaphore = asyncio.Semaphore(ORCHESTRATOR_MAX_CONCURRENT)

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
            return False, "INVALID_AUDIO_FORMAT"

        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            return False, "INVALID_AUDIO_FORMAT"

        return True, None

    def _validate_audio_duration(self, duration: float) -> None:
        """Validate audio duration is within limits.

        Args:
            duration: Audio duration in seconds

        Raises:
            OrchestratorError: If duration is out of range
        """
        if duration < ORCHESTRATOR_MIN_AUDIO_DURATION:
            min_dur = ORCHESTRATOR_MIN_AUDIO_DURATION
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.AUDIO_TOO_SHORT,
                message=f"Audio duration is too short (minimum {min_dur} seconds)",
                details={
                    "duration": duration,
                    "min_duration": min_dur,
                },
            )

        if duration > ORCHESTRATOR_MAX_AUDIO_DURATION:
            max_minutes = ORCHESTRATOR_MAX_AUDIO_DURATION / 60
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.AUDIO_TOO_LONG,
                message=f"Audio duration exceeds {max_minutes:.0f} minute limit",
                details={
                    "duration": duration,
                    "max_duration": ORCHESTRATOR_MAX_AUDIO_DURATION,
                },
            )

    async def process_dialogue(
        self,
        audio_data: bytes,
        filename: str,
        speed: float = 1.0,
    ) -> tuple[bytes, ProcessingMetadata]:
        """Process voice dialogue through STT → LLM → TTS pipeline.

        Args:
            audio_data: Raw audio file bytes
            filename: Original filename for format detection
            speed: TTS speech speed (0.5-2.0)

        Returns:
            Tuple of (WAV audio bytes, processing metadata)

        Raises:
            OrchestratorError: On any processing error
        """
        start_time = time.time()
        conversation_id = str(uuid.uuid4())

        # Validate format
        is_valid, error = self.validate_audio_format(filename, audio_data)
        if not is_valid:
            supported = ", ".join(sorted(f[1:].upper() for f in SUPPORTED_FORMATS))
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.INVALID_AUDIO_FORMAT,
                message=f"Unsupported audio format. Supported: {supported}",
            )

        # Check service availability before processing
        if not self._stt.model_loaded:
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.STT_SERVICE_UNAVAILABLE,
                message="STT service is not available",
            )

        if not self._llm.api_configured:
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.LLM_SERVICE_UNAVAILABLE,
                message="LLM service is not configured",
            )

        if not self._tts.is_ready:
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.TTS_SERVICE_UNAVAILABLE,
                message="TTS model is not loaded",
            )

        # Acquire semaphore for concurrency control
        try:
            async with asyncio.timeout(0.1):
                await self._semaphore.acquire()
        except TimeoutError:
            raise OrchestratorError(
                error_code=OrchestratorErrorCode.TOO_MANY_REQUESTS,
                message="Too many concurrent requests",
                retry_after=5,
            ) from None

        try:
            # Step 1: STT
            stt_start = time.time()
            try:
                stt_result = await self._stt.transcribe(audio_data, filename)
            except Exception as e:
                logger.exception("STT processing failed")
                raise OrchestratorError(
                    error_code=OrchestratorErrorCode.STT_SERVICE_UNAVAILABLE,
                    message=f"Speech recognition failed: {e}",
                ) from e
            stt_time = time.time() - stt_start

            # Validate transcription result
            recognized_text = stt_result.text.strip()
            if not recognized_text:
                raise OrchestratorError(
                    error_code=OrchestratorErrorCode.SPEECH_RECOGNITION_FAILED,
                    message="Could not recognize speech in the audio",
                )

            # Validate audio duration
            self._validate_audio_duration(stt_result.duration_seconds)

            logger.info(
                "STT completed",
                extra={
                    "text_length": len(recognized_text),
                    "duration": stt_result.duration_seconds,
                    "processing_time": stt_time,
                },
            )

            # Step 2: LLM
            llm_start = time.time()
            try:
                response_text, _ = await self._llm.generate_response(
                    message=recognized_text,
                    conversation_id=conversation_id,
                )
            except RuntimeError as e:
                error_msg = str(e)
                if "LLM_RATE_LIMITED" in error_msg:
                    raise OrchestratorError(
                        error_code=OrchestratorErrorCode.LLM_RATE_LIMITED,
                        message="LLM API rate limit exceeded",
                        retry_after=60,
                    ) from e
                if "LLM_CONNECTION_ERROR" in error_msg:
                    raise OrchestratorError(
                        error_code=OrchestratorErrorCode.LLM_CONNECTION_ERROR,
                        message="LLM API connection failed",
                    ) from e
                raise OrchestratorError(
                    error_code=OrchestratorErrorCode.LLM_SERVICE_UNAVAILABLE,
                    message=f"LLM processing failed: {e}",
                ) from e
            llm_time = time.time() - llm_start

            logger.info(
                "LLM completed",
                extra={
                    "input_length": len(recognized_text),
                    "output_length": len(response_text),
                    "processing_time": llm_time,
                },
            )

            # Step 3: TTS
            tts_start = time.time()
            try:
                sample_rate, audio = await self._tts.synthesize(response_text, speed)
            except ValueError as e:
                raise OrchestratorError(
                    error_code=OrchestratorErrorCode.SYNTHESIS_FAILED,
                    message=f"Speech synthesis failed: {e}",
                ) from e
            except Exception as e:
                logger.exception("TTS processing failed")
                raise OrchestratorError(
                    error_code=OrchestratorErrorCode.TTS_SERVICE_UNAVAILABLE,
                    message=f"TTS processing failed: {e}",
                ) from e
            tts_time = time.time() - tts_start

            # Convert to WAV bytes
            wav_bytes = self._tts.audio_to_wav_bytes(sample_rate, audio)
            output_duration = self._tts.get_audio_length_seconds(sample_rate, audio)

            logger.info(
                "TTS completed",
                extra={
                    "text_length": len(response_text),
                    "audio_duration": output_duration,
                    "processing_time": tts_time,
                },
            )

            total_time = time.time() - start_time

            metadata = ProcessingMetadata(
                total_time=total_time,
                stt_time=stt_time,
                llm_time=llm_time,
                tts_time=tts_time,
                input_duration=stt_result.duration_seconds,
                input_text_length=len(recognized_text),
                output_text_length=len(response_text),
                output_duration=output_duration,
                sample_rate=sample_rate,
            )

            logger.info(
                "Voice dialogue completed",
                extra={
                    "total_time": total_time,
                    "conversation_id": conversation_id,
                },
            )

            return wav_bytes, metadata

        finally:
            self._semaphore.release()

    def get_status(self) -> OrchestratorStatus:
        """Get orchestrator and service status.

        Returns:
            OrchestratorStatus with aggregated service health
        """
        from datetime import UTC, datetime

        # Get individual service statuses
        stt_status = self._stt.get_status()
        llm_status = self._llm.get_status()
        tts_status = self._tts.get_status()

        # Map to orchestrator status format
        services: dict[str, ServiceStatus] = {}

        # STT status
        if stt_status.model_loaded:
            stt_health = HealthStatus.HEALTHY
        else:
            stt_health = HealthStatus.UNHEALTHY
        services["stt"] = ServiceStatus(
            status=stt_health,
            details={
                "model_loaded": stt_status.model_loaded,
                "model_name": stt_status.model_name,
                "device": stt_status.device,
            },
        )

        # LLM status
        if llm_status.status.value == "healthy":
            llm_health = HealthStatus.HEALTHY
        elif llm_status.status.value == "degraded":
            llm_health = HealthStatus.DEGRADED
        else:
            llm_health = HealthStatus.UNHEALTHY
        llm_details: dict[str, object] = {
            "api_configured": llm_status.api_configured,
            "model": llm_status.model,
        }
        if llm_status.error_message:
            llm_details["last_error"] = llm_status.error_message
        services["llm"] = ServiceStatus(
            status=llm_health,
            details=llm_details,
        )

        # TTS status
        if tts_status.status.value == "healthy":
            tts_health = HealthStatus.HEALTHY
        elif tts_status.status.value == "degraded":
            tts_health = HealthStatus.DEGRADED
        else:
            tts_health = HealthStatus.UNHEALTHY
        services["tts"] = ServiceStatus(
            status=tts_health,
            details={
                "model_loaded": tts_status.model_loaded,
                "model_name": tts_status.model_name,
                "device": tts_status.device,
            },
        )

        # Determine overall status
        all_statuses = [s.status for s in services.values()]
        if all(s == HealthStatus.HEALTHY for s in all_statuses):
            overall = HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in all_statuses):
            overall = HealthStatus.UNHEALTHY
        else:
            overall = HealthStatus.DEGRADED

        return OrchestratorStatus(
            status=overall,
            services=services,
            timestamp=datetime.now(UTC),
        )
