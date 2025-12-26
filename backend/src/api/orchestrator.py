"""Voice Dialogue Orchestrator API endpoints."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import JSONResponse, Response

from src.config import TTS_MAX_SPEED, TTS_MIN_SPEED
from src.dependencies import get_orchestrator_service
from src.models.orchestrator import (
    OrchestratorErrorCode,
    OrchestratorErrorResponse,
    OrchestratorStatus,
)
from src.services.orchestrator_service import (
    OrchestratorError,
    OrchestratorService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/orchestrator", tags=["Orchestrator"])


def _error_code_to_status(error_code: OrchestratorErrorCode) -> int:
    """Map error code to HTTP status code."""
    mapping = {
        OrchestratorErrorCode.INVALID_AUDIO_FORMAT: 400,
        OrchestratorErrorCode.AUDIO_TOO_SHORT: 400,
        OrchestratorErrorCode.AUDIO_TOO_LONG: 400,
        OrchestratorErrorCode.SPEECH_RECOGNITION_FAILED: 422,
        OrchestratorErrorCode.STT_SERVICE_UNAVAILABLE: 503,
        OrchestratorErrorCode.LLM_SERVICE_UNAVAILABLE: 503,
        OrchestratorErrorCode.LLM_RATE_LIMITED: 429,
        OrchestratorErrorCode.LLM_CONNECTION_ERROR: 503,
        OrchestratorErrorCode.TTS_SERVICE_UNAVAILABLE: 503,
        OrchestratorErrorCode.SYNTHESIS_FAILED: 500,
        OrchestratorErrorCode.PROCESSING_TIMEOUT: 504,
        OrchestratorErrorCode.TOO_MANY_REQUESTS: 429,
    }
    return mapping.get(error_code, 500)


@router.post(
    "/dialogue",
    response_class=Response,
    responses={
        200: {
            "description": "Audio response",
            "content": {"audio/wav": {}},
        },
        400: {
            "description": "Invalid request",
            "model": OrchestratorErrorResponse,
        },
        422: {
            "description": "Processing failed",
            "model": OrchestratorErrorResponse,
        },
        429: {
            "description": "Rate limited",
            "model": OrchestratorErrorResponse,
        },
        503: {
            "description": "Service unavailable",
            "model": OrchestratorErrorResponse,
        },
    },
)
async def execute_dialogue(
    audio: Annotated[UploadFile, File(description="Audio file (WAV, MP3, etc.)")],
    speed: Annotated[
        float,
        Form(ge=TTS_MIN_SPEED, le=TTS_MAX_SPEED, description="TTS speech speed"),
    ] = 1.0,
    service: Annotated[
        OrchestratorService, Depends(get_orchestrator_service)
    ] = None,  # type: ignore[assignment]
) -> Response:
    """Execute voice dialogue.

    Accepts audio input, processes through STT → LLM → TTS pipeline,
    and returns audio response with processing metadata in headers.
    """
    # Read audio data
    audio_data = await audio.read()
    filename = audio.filename or "audio.wav"

    try:
        wav_bytes, metadata = await service.process_dialogue(
            audio_data=audio_data,
            filename=filename,
            speed=speed,
        )
    except OrchestratorError as e:
        logger.warning(
            "Dialogue processing failed: %s - %s",
            e.error_code.value,
            e.message,
        )
        error_response = OrchestratorErrorResponse(
            error_code=e.error_code,
            message=e.message,
            details=e.details,
            retry_after=e.retry_after,
        )
        return JSONResponse(
            status_code=_error_code_to_status(e.error_code),
            content=error_response.model_dump(),
        )

    # Build response with metadata headers
    headers = {
        "X-Processing-Time-Total": f"{metadata.total_time:.3f}",
        "X-Processing-Time-STT": f"{metadata.stt_time:.3f}",
        "X-Processing-Time-LLM": f"{metadata.llm_time:.3f}",
        "X-Processing-Time-TTS": f"{metadata.tts_time:.3f}",
        "X-Input-Duration": f"{metadata.input_duration:.3f}",
        "X-Input-Text-Length": str(metadata.input_text_length),
        "X-Output-Text-Length": str(metadata.output_text_length),
        "X-Output-Duration": f"{metadata.output_duration:.3f}",
        "X-Sample-Rate": str(metadata.sample_rate),
    }

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers=headers,
    )


@router.get(
    "/status",
    response_model=OrchestratorStatus,
)
async def get_status(
    service: Annotated[
        OrchestratorService, Depends(get_orchestrator_service)
    ] = None,  # type: ignore[assignment]
) -> OrchestratorStatus:
    """Get orchestrator status.

    Returns health status of the orchestrator and all underlying services
    (STT, LLM, TTS).
    """
    return service.get_status()
