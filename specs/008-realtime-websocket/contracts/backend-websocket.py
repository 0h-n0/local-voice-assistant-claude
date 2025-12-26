"""
WebSocket Message Contracts for Backend.

Feature: 008-realtime-websocket
Date: 2025-12-27

These Pydantic models define the WebSocket message protocol.
Place in: backend/src/models/websocket.py
"""

from datetime import datetime
from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================


class ProcessingStatus(str, Enum):
    """Processing pipeline stages."""

    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    SYNTHESIZING = "synthesizing"
    PLAYING = "playing"
    ERROR = "error"


class WebSocketErrorCode(str, Enum):
    """WebSocket-specific error codes."""

    # Connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    CONNECTION_CLOSED = "CONNECTION_CLOSED"

    # STT errors
    STT_SERVICE_ERROR = "STT_SERVICE_ERROR"
    STT_TIMEOUT = "STT_TIMEOUT"
    AUDIO_TOO_SHORT = "AUDIO_TOO_SHORT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"

    # LLM errors
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"

    # TTS errors
    TTS_SERVICE_ERROR = "TTS_SERVICE_ERROR"
    TTS_TIMEOUT = "TTS_TIMEOUT"

    # General errors
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AudioFormat(str, Enum):
    """Supported audio formats for streaming."""

    PCM16 = "pcm16"
    OPUS = "opus"
    WEBM = "webm"


# ============================================================================
# Server -> Client Messages
# ============================================================================


class TranscriptPartialMessage(BaseModel):
    """Partial transcript during speech recognition."""

    type: Literal["transcript_partial"] = "transcript_partial"
    content: str
    confidence: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class TranscriptFinalMessage(BaseModel):
    """Final transcript after speech recognition completes."""

    type: Literal["transcript_final"] = "transcript_final"
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    duration_ms: int = Field(ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class StatusUpdateMessage(BaseModel):
    """Processing status update."""

    type: Literal["status_update"] = "status_update"
    status: ProcessingStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ResponseChunkMessage(BaseModel):
    """LLM response chunk during streaming."""

    type: Literal["response_chunk"] = "response_chunk"
    content: str
    chunk_index: int = Field(ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ResponseCompleteMessage(BaseModel):
    """Response complete notification."""

    type: Literal["response_complete"] = "response_complete"
    full_text: str
    audio_available: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ErrorMessage(BaseModel):
    """Error notification."""

    type: Literal["error"] = "error"
    code: WebSocketErrorCode
    message: str
    details: dict | None = None
    recoverable: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class ConnectionAckMessage(BaseModel):
    """Connection acknowledgement after successful handshake."""

    type: Literal["connection_ack"] = "connection_ack"
    session_id: str
    server_time: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


class PingMessage(BaseModel):
    """Server ping for keepalive."""

    type: Literal["ping"] = "ping"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


# Union type for all server messages
ServerMessage = Union[
    TranscriptPartialMessage,
    TranscriptFinalMessage,
    StatusUpdateMessage,
    ResponseChunkMessage,
    ResponseCompleteMessage,
    ErrorMessage,
    ConnectionAckMessage,
    PingMessage,
]


# ============================================================================
# Client -> Server Messages
# ============================================================================


class AudioChunkMessage(BaseModel):
    """Audio chunk during voice recording."""

    type: Literal["audio_chunk"] = "audio_chunk"
    data: str  # Base64 encoded audio data
    chunk_index: int = Field(ge=0)
    sample_rate: int = Field(default=16000, ge=8000, le=48000)
    format: AudioFormat = AudioFormat.PCM16


class AudioEndMessage(BaseModel):
    """Signal that audio stream has ended."""

    type: Literal["audio_end"] = "audio_end"
    total_chunks: int = Field(ge=0)
    total_duration_ms: int = Field(ge=0, le=60000)  # Max 60 seconds


class TextInputMessage(BaseModel):
    """Text input (alternative to voice)."""

    type: Literal["text_input"] = "text_input"
    content: str = Field(min_length=1, max_length=10000)
    conversation_id: str | None = None


class CancelMessage(BaseModel):
    """Cancel current operation."""

    type: Literal["cancel"] = "cancel"
    reason: str | None = None


class PongMessage(BaseModel):
    """Response to server ping."""

    type: Literal["pong"] = "pong"
    timestamp: datetime

    model_config = {"json_encoders": {datetime: lambda v: v.isoformat()}}


# Union type for all client messages
ClientMessage = Union[
    AudioChunkMessage,
    AudioEndMessage,
    TextInputMessage,
    CancelMessage,
    PongMessage,
]


# ============================================================================
# Message Parsing Helpers
# ============================================================================


def parse_client_message(data: dict) -> ClientMessage:
    """Parse incoming client message based on type field."""
    message_type = data.get("type")

    parsers = {
        "audio_chunk": AudioChunkMessage,
        "audio_end": AudioEndMessage,
        "text_input": TextInputMessage,
        "cancel": CancelMessage,
        "pong": PongMessage,
    }

    parser = parsers.get(message_type)
    if parser is None:
        raise ValueError(f"Unknown message type: {message_type}")

    return parser.model_validate(data)
