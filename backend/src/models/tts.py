"""Pydantic models for TTS API."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TTSSynthesisRequest(BaseModel):
    """TTS synthesis request model."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Japanese text to synthesize",
        examples=["こんにちは、音声アシスタントです。"],
    )

    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed scale (0.5=slow, 1.0=normal, 2.0=fast)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "こんにちは",
                "speed": 1.0,
            }
        }
    )


class TTSErrorCode(str, Enum):
    """TTS error codes."""

    EMPTY_TEXT = "EMPTY_TEXT"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_SPEED = "INVALID_SPEED"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    SYNTHESIS_FAILED = "SYNTHESIS_FAILED"
    SERVICE_BUSY = "SERVICE_BUSY"


class TTSErrorResponse(BaseModel):
    """TTS error response model."""

    error_code: TTSErrorCode = Field(
        ...,
        description="Machine-readable error code",
    )

    message: str = Field(
        ...,
        description="Human-readable error message",
    )

    details: dict[str, Any] | None = Field(
        default=None,
        description="Additional error information",
    )


class TTSHealthStatus(str, Enum):
    """TTS service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class TTSStatus(BaseModel):
    """TTS service status model."""

    status: TTSHealthStatus = Field(
        ...,
        description="Service health status",
    )

    model_loaded: bool = Field(
        ...,
        description="Whether the TTS model is loaded",
    )

    model_name: str | None = Field(
        default=None,
        description="Name of the loaded model",
    )

    device: str = Field(
        ...,
        description="Inference device (cpu/cuda)",
    )

    last_check: datetime = Field(
        ...,
        description="Last health check timestamp",
    )

    error_message: str | None = Field(
        default=None,
        description="Error details if status is not healthy",
    )
