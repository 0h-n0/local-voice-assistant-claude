"""Pydantic models for Voice Dialogue Orchestrator."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OrchestratorErrorCode(str, Enum):
    """Orchestrator error codes."""

    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_SHORT = "AUDIO_TOO_SHORT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    SPEECH_RECOGNITION_FAILED = "SPEECH_RECOGNITION_FAILED"
    STT_SERVICE_UNAVAILABLE = "STT_SERVICE_UNAVAILABLE"
    LLM_SERVICE_UNAVAILABLE = "LLM_SERVICE_UNAVAILABLE"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"
    LLM_CONNECTION_ERROR = "LLM_CONNECTION_ERROR"
    TTS_SERVICE_UNAVAILABLE = "TTS_SERVICE_UNAVAILABLE"
    SYNTHESIS_FAILED = "SYNTHESIS_FAILED"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"


class OrchestratorErrorResponse(BaseModel):
    """Orchestrator error response."""

    error_code: OrchestratorErrorCode
    message: str
    details: dict[str, Any] | None = None
    retry_after: int | None = None


class HealthStatus(str, Enum):
    """Health status enum."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ProcessingMetadata(BaseModel):
    """Processing metadata for response headers."""

    total_time: float
    stt_time: float
    llm_time: float
    tts_time: float
    input_duration: float
    input_text_length: int
    output_text_length: int
    output_duration: float
    sample_rate: int


class ServiceStatus(BaseModel):
    """Individual service status."""

    status: HealthStatus
    details: dict[str, Any] = Field(default_factory=dict)


class OrchestratorStatus(BaseModel):
    """Orchestrator status response."""

    status: HealthStatus
    services: dict[str, ServiceStatus]
    timestamp: datetime
