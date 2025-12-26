# Data Model: LLM Text Response Service

**Feature**: 003-llm-text-service
**Date**: 2025-12-26

## Entities

### ChatMessage

Represents a single message in a conversation (user or assistant).

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `role` | enum | Yes | `user`, `assistant` | Who sent the message |
| `content` | string | Yes | 1-4000 chars | Message text content |
| `timestamp` | datetime | Yes | ISO 8601 | When message was created |

**Validation Rules**:
- `content` must not be empty or whitespace-only
- `content` must not exceed 4000 characters
- `role` must be valid enum value

### Conversation

A collection of messages with shared context.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `id` | string | Yes | 1-64 chars, alphanumeric + hyphen/underscore | Client-generated conversation ID |
| `messages` | list[ChatMessage] | No | Max 20 messages | Conversation history |
| `created_at` | datetime | Yes | ISO 8601 | When conversation started |
| `updated_at` | datetime | Yes | ISO 8601 | Last activity time |

**State Transitions**:
- **Created**: First message received with new conversation ID
- **Active**: Messages being added, updated_at refreshed
- **Expired**: TTL exceeded (60 minutes default), automatically removed

**Validation Rules**:
- `id` must match pattern `^[a-zA-Z0-9_-]{1,64}$`
- When `messages` exceeds 20, oldest messages are trimmed (FIFO)

### LLMRequest

API request for generating a response.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `message` | string | Yes | 1-4000 chars | User's input text |
| `conversation_id` | string | Yes | 1-64 chars | Client-generated conversation ID |

### LLMResponse

API response with generated text.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `text` | string | Yes | Non-empty | Generated response text |
| `conversation_id` | string | Yes | - | Echo of request conversation ID |
| `usage` | TokenUsage | No | - | Token usage statistics |
| `processing_time_seconds` | float | Yes | ≥0 | Total processing time |

### TokenUsage

Token consumption details from LLM call.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `prompt_tokens` | int | Yes | ≥0 | Tokens in prompt (including history) |
| `completion_tokens` | int | Yes | ≥0 | Tokens in response |
| `total_tokens` | int | Yes | ≥0 | Sum of prompt + completion |

### LLMStatus

Service health status.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `status` | enum | Yes | `healthy`, `degraded`, `unhealthy` | Overall service health |
| `model` | string | Yes | - | Configured LLM model name |
| `api_configured` | bool | Yes | - | Whether API key is set |
| `active_conversations` | int | Yes | ≥0 | Number of active conversations |
| `last_check` | datetime | No | ISO 8601 | Last health check timestamp |
| `error_message` | string | No | - | Error details if unhealthy |

**Status Definitions**:
- `healthy`: API key configured, recent successful call or startup
- `degraded`: API key configured but experiencing intermittent errors
- `unhealthy`: API key missing or persistent connection failures

### ErrorResponse

Standard error response format (shared with STT API).

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `error_code` | enum | Yes | See error codes | Machine-readable error code |
| `message` | string | Yes | - | Human-readable error message |
| `details` | object | No | - | Additional error context |

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `EMPTY_MESSAGE` | 400 | Message content is empty or whitespace |
| `MESSAGE_TOO_LONG` | 400 | Message exceeds 4000 character limit |
| `INVALID_CONVERSATION_ID` | 400 | Conversation ID format invalid |
| `LLM_NOT_CONFIGURED` | 503 | OpenAI API key not configured |
| `LLM_RATE_LIMITED` | 503 | Rate limited by OpenAI |
| `LLM_CONNECTION_ERROR` | 503 | Cannot connect to OpenAI API |
| `LLM_API_ERROR` | 500 | OpenAI API returned an error |
| `LLM_PROCESSING_ERROR` | 500 | Internal processing error |

## Relationships

```
Conversation (1) ──── contains ────> (N) ChatMessage

LLMRequest ──── creates/updates ────> Conversation
             ──── produces ────> LLMResponse

ConversationCache ──── manages ────> (N) Conversation
```

## Pydantic Models (Implementation Reference)

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
import re

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=4000)
    timestamp: datetime = Field(default_factory=datetime.now)

class LLMRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: str = Field(..., min_length=1, max_length=64)

    @field_validator("conversation_id")
    @classmethod
    def validate_conversation_id(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("conversation_id must be alphanumeric with hyphens/underscores")
        return v

    @field_validator("message")
    @classmethod
    def validate_message_not_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message cannot be empty or whitespace only")
        return v

class TokenUsage(BaseModel):
    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)

class LLMResponse(BaseModel):
    text: str
    conversation_id: str
    usage: TokenUsage | None = None
    processing_time_seconds: float = Field(..., ge=0)

class ServiceStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class LLMStatus(BaseModel):
    status: ServiceStatus
    model: str
    api_configured: bool
    active_conversations: int = Field(..., ge=0)
    last_check: datetime | None = None
    error_message: str | None = None
```
