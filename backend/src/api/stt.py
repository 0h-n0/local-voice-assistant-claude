"""STT API endpoints for Japanese speech-to-text."""

import logging
import re
import time

from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    WebSocket,
    WebSocketDisconnect,
    status,
)

from src.dependencies import get_stt_service
from src.models.stt import (
    ErrorCode,
    ErrorResponse,
    StreamMessage,
    STTStatus,
    TranscriptionResponse,
)
from src.services.stt_service import AudioBuffer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/stt", tags=["stt"])

# Maximum file size: 100MB
MAX_FILE_SIZE_MB = 100
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024

# Chunk size for streaming file read (1MB)
CHUNK_SIZE = 1024 * 1024


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe logging (prevent log injection)."""
    # Remove control characters and limit length
    sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)
    return sanitized[:255] if len(sanitized) > 255 else sanitized


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        413: {"model": ErrorResponse, "description": "File too large"},
        500: {"model": ErrorResponse, "description": "Processing error"},
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
)
async def transcribe_audio(file: UploadFile) -> TranscriptionResponse:
    """Transcribe an audio file to Japanese text.

    Accepts WAV, MP3, FLAC, and OGG formats.
    Maximum file size: 100MB.
    """
    raw_filename = file.filename or "audio.wav"
    filename = _sanitize_filename(raw_filename)
    logger.info("Transcription request received: filename=%s", filename)
    request_start = time.time()

    stt_service = get_stt_service()

    # Check if model is loaded
    if not stt_service.model_loaded:
        logger.warning("Transcription rejected: model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error_code=ErrorCode.MODEL_NOT_LOADED,
                message="STT model is still loading, please try again later",
            ).model_dump(),
        )

    # Read file content with size limit check (stream to avoid memory issues)
    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE:
            file_size_mb = total_size / (1024 * 1024)
            logger.warning(
                "Transcription rejected: file too large (>%.2f MB > %d MB)",
                file_size_mb,
                MAX_FILE_SIZE_MB,
            )
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=ErrorResponse(
                    error_code=ErrorCode.FILE_TOO_LARGE,
                    message=f"File size exceeds maximum limit of {MAX_FILE_SIZE_MB}MB",
                    details={
                        "max_size_mb": MAX_FILE_SIZE_MB,
                        "provided_size_mb": file_size_mb,
                    },
                ).model_dump(),
            )
        chunks.append(chunk)

    content = b"".join(chunks)
    file_size_mb = len(content) / (1024 * 1024)
    logger.debug("File size: %.2f MB", file_size_mb)

    # Validate format
    is_valid, error_code = stt_service.validate_audio_format(filename, content)
    if not is_valid:
        if error_code == "UNSUPPORTED_FORMAT":
            from pathlib import Path

            ext = Path(filename).suffix.lower()
            logger.warning("Transcription rejected: unsupported format %s", ext)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.UNSUPPORTED_FORMAT,
                    message=f"File format '{ext}' is not supported",
                    details={
                        "provided_format": ext,
                        "supported_formats": ["wav", "mp3", "flac", "ogg"],
                    },
                ).model_dump(),
            )
        if error_code == "EMPTY_AUDIO":
            logger.warning("Transcription rejected: empty audio content")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.EMPTY_AUDIO,
                    message="Audio file is empty or invalid",
                ).model_dump(),
            )

    # Transcribe
    try:
        logger.debug("Starting transcription for %s", filename)
        result = await stt_service.transcribe(content, filename)
        total_time = time.time() - request_start
        logger.info(
            "Transcription completed: filename=%s, duration=%.2fs, "
            "processing_time=%.2fs, text_length=%d",
            filename,
            result.duration_seconds,
            total_time,
            len(result.text),
        )
        return result
    except ValueError as e:
        error_str = str(e)
        if "EMPTY_AUDIO" in error_str:
            logger.warning("Transcription failed: empty audio - %s", filename)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.EMPTY_AUDIO,
                    message="Audio file is empty or invalid",
                ).model_dump(),
            ) from e
        if "UNSUPPORTED_FORMAT" in error_str:
            logger.warning("Transcription failed: unsupported format - %s", filename)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.UNSUPPORTED_FORMAT,
                    message="Unsupported audio format",
                ).model_dump(),
            ) from e
        logger.error("Transcription failed: validation error - %s: %s", filename, e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error_code=ErrorCode.PROCESSING_ERROR,
                message=str(e),
            ).model_dump(),
        ) from e
    except RuntimeError as e:
        if "MODEL_NOT_LOADED" in str(e):
            logger.error("Transcription failed: model not loaded - %s", filename)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error_code=ErrorCode.MODEL_NOT_LOADED,
                    message="STT model is not loaded",
                ).model_dump(),
            ) from e
        logger.exception("Processing error during transcription: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error_code=ErrorCode.PROCESSING_ERROR,
                message="Failed to process audio file",
            ).model_dump(),
        ) from e
    except Exception as e:
        logger.exception("Unexpected error during transcription: %s", filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error_code=ErrorCode.PROCESSING_ERROR,
                message="An unexpected error occurred",
            ).model_dump(),
        ) from e


@router.websocket("/stream")
async def stream_transcribe(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time audio streaming transcription.

    Accepts 16kHz, 16-bit PCM audio chunks and returns partial/final
    transcription results.
    """
    logger.info("WebSocket stream connection request received")
    await websocket.accept()
    logger.debug("WebSocket connection accepted")

    try:
        stt_service = get_stt_service()
    except RuntimeError:
        logger.error("WebSocket rejected: STT service not initialized")
        await websocket.send_json(
            StreamMessage(
                type="error",
                text="STT service not initialized",
                is_final=True,
                timestamp=time.time(),
            ).model_dump()
        )
        await websocket.close()
        return

    if not stt_service.model_loaded:
        logger.warning("WebSocket rejected: model not loaded")
        await websocket.send_json(
            StreamMessage(
                type="error",
                text="STT model is still loading",
                is_final=True,
                timestamp=time.time(),
            ).model_dump()
        )
        await websocket.close()
        return

    buffer = AudioBuffer(min_samples=16000)  # 1 second of audio
    chunks_received = 0
    transcriptions_sent = 0
    session_start = time.time()

    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            buffer.add(data)
            chunks_received += 1

            # Process when we have enough data
            if buffer.should_process():
                try:
                    process_start = time.time()
                    text = await stt_service.transcribe_pcm(buffer.get_data())
                    process_time = time.time() - process_start
                    transcriptions_sent += 1
                    logger.debug(
                        "Stream transcription: text_length=%d, process_time=%.2fs",
                        len(text),
                        process_time,
                    )
                    await websocket.send_json(
                        StreamMessage(
                            type="partial",
                            text=text,
                            is_final=False,
                            timestamp=time.time(),
                        ).model_dump()
                    )
                    buffer.clear()
                except Exception as e:
                    logger.exception("Error during streaming transcription")
                    await websocket.send_json(
                        StreamMessage(
                            type="error",
                            text=str(e),
                            is_final=False,
                            timestamp=time.time(),
                        ).model_dump()
                    )

    except WebSocketDisconnect:
        session_duration = time.time() - session_start
        logger.info(
            "WebSocket client disconnected: session_duration=%.2fs, "
            "chunks=%d, transcriptions=%d",
            session_duration,
            chunks_received,
            transcriptions_sent,
        )
        # Process any remaining audio in buffer
        if not buffer.is_empty():
            try:
                text = await stt_service.transcribe_pcm(buffer.get_data())
                # Can't send after disconnect, but we processed it
                logger.debug("Final transcription (after disconnect): %s", text)
            except Exception:
                pass
    except Exception as e:
        session_duration = time.time() - session_start
        logger.exception(
            "WebSocket error after %.2fs, chunks=%d",
            session_duration,
            chunks_received,
        )
        import contextlib

        with contextlib.suppress(Exception):
            await websocket.send_json(
                StreamMessage(
                    type="error",
                    text=str(e),
                    is_final=True,
                    timestamp=time.time(),
                ).model_dump()
            )
        await websocket.close()


@router.get(
    "/status",
    response_model=STTStatus,
    responses={
        503: {"model": ErrorResponse, "description": "Model not loaded"},
    },
)
async def get_status() -> STTStatus:
    """Get the current status of the STT service.

    Returns model load status, device information, and memory usage.
    """
    logger.debug("Status request received")
    try:
        stt_service = get_stt_service()
    except RuntimeError as e:
        logger.warning("Status request failed: STT service not initialized")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error_code=ErrorCode.MODEL_NOT_LOADED,
                message="STT service not initialized",
            ).model_dump(),
        ) from e

    stt_status = stt_service.get_status()
    logger.debug(
        "Status: model_loaded=%s, device=%s, memory=%.2fMB",
        stt_status.model_loaded,
        stt_status.device,
        stt_status.memory_usage_mb,
    )
    return stt_status
