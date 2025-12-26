"""TTS API endpoints."""

import logging
import time
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from src.dependencies import get_tts_service
from src.models.tts import (
    TTSErrorCode,
    TTSErrorResponse,
    TTSStatus,
    TTSSynthesisRequest,
)
from src.services.tts_service import TTSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tts", tags=["TTS"])


def error_response(
    error_code: TTSErrorCode,
    message: str,
    status_code: int,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Create a JSON error response."""
    return JSONResponse(
        status_code=status_code,
        content=TTSErrorResponse(
            error_code=error_code,
            message=message,
            details=details,
        ).model_dump(),
    )


@router.post(
    "/synthesize",
    responses={
        200: {
            "content": {"audio/wav": {}},
            "description": "Successfully synthesized audio",
        },
        400: {"model": TTSErrorResponse, "description": "Invalid request"},
        503: {"model": TTSErrorResponse, "description": "Service unavailable"},
    },
)
async def synthesize(
    request: TTSSynthesisRequest,
    tts_service: Annotated[TTSService, Depends(get_tts_service)],
) -> Response:
    """Synthesize speech from Japanese text.

    Returns WAV audio file with metadata in headers.
    """
    start_time = time.time()

    # Check if service is ready
    if not tts_service.is_ready:
        return error_response(
            TTSErrorCode.MODEL_NOT_LOADED,
            "TTS model is not loaded",
            503,
        )

    # Validate text
    try:
        cleaned_text = tts_service.validate_text(request.text)
    except ValueError as e:
        error_msg = str(e).lower()
        if "empty" in error_msg:
            return error_response(
                TTSErrorCode.EMPTY_TEXT,
                "Text content is empty or whitespace only",
                400,
            )
        elif "too long" in error_msg:
            return error_response(
                TTSErrorCode.TEXT_TOO_LONG,
                "Text exceeds 5000 character limit",
                400,
                details={"max_length": 5000, "provided_length": len(request.text)},
            )
        else:
            return error_response(
                TTSErrorCode.SYNTHESIS_FAILED,
                str(e),
                400,
            )

    # Synthesize audio
    try:
        sample_rate, audio = await tts_service.synthesize(
            cleaned_text, request.speed
        )
    except TimeoutError:
        return error_response(
            TTSErrorCode.SERVICE_BUSY,
            "Service is processing too many requests",
            503,
        )
    except RuntimeError as e:
        if "not loaded" in str(e).lower():
            return error_response(
                TTSErrorCode.MODEL_NOT_LOADED,
                "TTS model is not loaded",
                503,
            )
        return error_response(
            TTSErrorCode.SYNTHESIS_FAILED,
            f"Failed to synthesize audio: {e}",
            500,
        )
    except Exception as e:
        logger.exception("Synthesis failed")
        return error_response(
            TTSErrorCode.SYNTHESIS_FAILED,
            f"Failed to synthesize audio: {e}",
            500,
        )

    # Convert to WAV bytes
    wav_bytes = tts_service.audio_to_wav_bytes(sample_rate, audio)
    audio_length = tts_service.get_audio_length_seconds(sample_rate, audio)
    processing_time = time.time() - start_time

    logger.info(
        f"Synthesized {len(cleaned_text)} chars in {processing_time:.2f}s "
        f"({audio_length:.2f}s audio)"
    )

    return Response(
        content=wav_bytes,
        media_type="audio/wav",
        headers={
            "X-Processing-Time": f"{processing_time:.3f}",
            "X-Audio-Length": f"{audio_length:.3f}",
            "X-Sample-Rate": str(sample_rate),
        },
    )


@router.get(
    "/status",
    response_model=TTSStatus,
    responses={
        200: {"model": TTSStatus, "description": "Service status"},
    },
)
async def get_status(
    tts_service: Annotated[TTSService, Depends(get_tts_service)],
) -> TTSStatus:
    """Get TTS service status.

    Returns current health status and model information.
    """
    return tts_service.get_status()
