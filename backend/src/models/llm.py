"""LLM service Pydantic models and error codes."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ErrorCode(str, Enum):
    """Error codes for LLM service."""

    EMPTY_MESSAGE = "EMPTY_MESSAGE"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    INVALID_CONVERSATION_ID = "INVALID_CONVERSATION_ID"
    LLM_NOT_CONFIGURED = "LLM_NOT_CONFIGURED"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"
    LLM_CONNECTION_ERROR = "LLM_CONNECTION_ERROR"
    LLM_API_ERROR = "LLM_API_ERROR"
    LLM_PROCESSING_ERROR = "LLM_PROCESSING_ERROR"


class ServiceStatus(str, Enum):
    """LLM service health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ErrorResponse(BaseModel):
    """Standard error response for LLM API."""

    error_code: ErrorCode
    message: str
    details: dict[str, object] | None = None


class TokenUsage(BaseModel):
    """Token usage statistics from LLM call."""

    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class LLMRequest(BaseModel):
    """Request model for LLM chat endpoint."""

    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str = Field(..., min_length=1, max_length=64)


class LLMResponse(BaseModel):
    """Response model for LLM chat endpoint."""

    text: str
    conversation_id: str
    usage: TokenUsage | None = None
    processing_time_seconds: float = Field(..., ge=0)


class LLMStatus(BaseModel):
    """LLM service health status response."""

    status: ServiceStatus
    model: str
    api_configured: bool
    active_conversations: int = Field(..., ge=0)
    last_check: datetime | None = None
    error_message: str | None = None
