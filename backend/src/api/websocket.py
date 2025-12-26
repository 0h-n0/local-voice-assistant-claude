"""WebSocket API Endpoint.

Real-time WebSocket endpoint for voice dialogue processing.
Handles audio streaming, transcription, LLM responses, and status updates.
"""

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from src.config import WS_HEARTBEAT_INTERVAL
from src.lib.websocket_manager import connection_manager
from src.models.websocket import (
    AudioChunkMessage,
    AudioEndMessage,
    CancelMessage,
    ClientMessage,
    PongMessage,
    ProcessingStatus,
    TextInputMessage,
    WebSocketErrorCode,
    parse_client_message,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/realtime")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint for real-time voice dialogue.

    Protocol:
        1. Client connects, receives connection_ack with session_id
        2. Client sends audio_chunk messages while recording
        3. Client sends audio_end when recording stops
        4. Server sends transcript_partial/transcript_final during STT
        5. Server sends status_update at each processing stage
        6. Server sends response_chunk during LLM streaming
        7. Server sends response_complete when done
        8. Server sends ping periodically, client responds with pong
    """
    session_id = await connection_manager.connect(websocket)
    logger.info("WebSocket connected: %s", session_id)

    # Start ping loop for keepalive
    await connection_manager.start_ping_loop(session_id, WS_HEARTBEAT_INTERVAL)

    try:
        # Set initial status to idle
        await connection_manager.send_status_update(session_id, ProcessingStatus.IDLE)

        while True:
            # Receive message from client
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
                message = parse_client_message(data)
            except json.JSONDecodeError:
                await connection_manager.send_error(
                    session_id,
                    WebSocketErrorCode.INVALID_MESSAGE,
                    "Invalid JSON format",
                    recoverable=True,
                )
                continue
            except (ValidationError, ValueError) as e:
                await connection_manager.send_error(
                    session_id,
                    WebSocketErrorCode.INVALID_MESSAGE,
                    f"Invalid message: {e!s}",
                    recoverable=True,
                )
                continue

            # Handle message based on type
            await handle_client_message(session_id, message)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
    except Exception as e:
        logger.exception("WebSocket error for session %s: %s", session_id, e)
        await connection_manager.send_error(
            session_id,
            WebSocketErrorCode.INTERNAL_ERROR,
            "Internal server error",
            recoverable=False,
        )
    finally:
        await connection_manager.disconnect(session_id)


async def handle_client_message(
    session_id: str,
    message: ClientMessage,
) -> None:
    """Handle incoming client message.

    Args:
        session_id: The session ID.
        message: The parsed client message.
    """
    if isinstance(message, AudioChunkMessage):
        await handle_audio_chunk(session_id, message)
    elif isinstance(message, AudioEndMessage):
        await handle_audio_end(session_id, message)
    elif isinstance(message, TextInputMessage):
        await handle_text_input(session_id, message)
    elif isinstance(message, CancelMessage):
        await handle_cancel(session_id, message)
    elif isinstance(message, PongMessage):
        # Pong received, no action needed (heartbeat confirmed)
        logger.debug("Pong received from session %s", session_id)
    else:
        logger.warning("Unknown message type from session %s: %s", session_id, message)


async def handle_audio_chunk(
    session_id: str,
    message: AudioChunkMessage,
) -> None:
    """Handle audio chunk message.

    TODO: Implement in Phase 3 (US1) - forward to StreamingSTTService.

    Args:
        session_id: The session ID.
        message: The audio chunk message.
    """
    # Placeholder - will be implemented in Phase 3
    _ = message  # Suppress unused warning until implementation
    logger.debug("Audio chunk received for session %s", session_id)


async def handle_audio_end(
    session_id: str,
    message: AudioEndMessage,
) -> None:
    """Handle audio end message.

    TODO: Implement in Phase 3 (US1) - finalize STT and trigger LLM.

    Args:
        session_id: The session ID.
        message: The audio end message.
    """
    # Placeholder - will be implemented in Phase 3
    _ = message  # Suppress unused warning until implementation
    logger.debug("Audio end received for session %s", session_id)


async def handle_text_input(
    session_id: str,
    message: TextInputMessage,
) -> None:
    """Handle text input message.

    TODO: Implement in Phase 5 (US3) - forward to LLM service.

    Args:
        session_id: The session ID.
        message: The text input message.
    """
    # Placeholder - will be implemented in Phase 5
    _ = message  # Suppress unused warning until implementation
    logger.debug("Text input received for session %s", session_id)


async def handle_cancel(
    session_id: str,
    message: CancelMessage,
) -> None:
    """Handle cancel message.

    TODO: Implement in Phase 7 - abort ongoing STT/LLM operations.

    Args:
        session_id: The session ID.
        message: The cancel message.
    """
    # Placeholder - will be implemented in Phase 7
    _ = message  # Suppress unused warning until implementation
    logger.debug("Cancel received for session %s", session_id)
    await connection_manager.send_status_update(session_id, ProcessingStatus.IDLE)
