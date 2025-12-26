"""Pydantic models for conversation history storage."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """Message sender role."""

    USER = "user"
    ASSISTANT = "assistant"


class MessageCreate(BaseModel):
    """Internal model for creating messages (from orchestrator)."""

    conversation_id: str
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    """Message in API response."""

    id: int
    role: MessageRole
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    """Conversation in list response."""

    id: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class ConversationDetail(BaseModel):
    """Full conversation with messages."""

    id: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """Paginated conversation list."""

    conversations: list[ConversationSummary]
    total: int
    limit: int
    offset: int


class ConversationErrorCode(str, Enum):
    """Error codes for conversation operations."""

    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    DATABASE_ERROR = "DATABASE_ERROR"


class ConversationErrorResponse(BaseModel):
    """Error response for conversation operations."""

    error_code: ConversationErrorCode
    message: str
    details: dict[str, Any] | None = None
