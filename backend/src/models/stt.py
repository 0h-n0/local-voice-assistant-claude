"""Pydantic models for STT API."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Error codes for STT API."""

    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    EMPTY_AUDIO = "EMPTY_AUDIO"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    PROCESSING_ERROR = "PROCESSING_ERROR"


class Segment(BaseModel):
    """Text segment with timestamps."""

    text: str
    start_time: float = Field(ge=0)
    end_time: float


class TranscriptionResponse(BaseModel):
    """Response model for transcription results."""

    text: str
    duration_seconds: float = Field(ge=0)
    processing_time_seconds: float = Field(ge=0)
    segments: list[Segment] | None = None


class STTStatus(BaseModel):
    """STT service status model."""

    model_loaded: bool
    model_name: str
    device: Literal["cuda", "cpu"]
    memory_usage_mb: float


class StreamMessage(BaseModel):
    """WebSocket streaming message."""

    type: Literal["partial", "final", "error"]
    text: str
    is_final: bool
    timestamp: float | None = None


class ErrorResponse(BaseModel):
    """Error response model."""

    error_code: str
    message: str
    details: dict[str, str | int | float | list[str]] | None = None
