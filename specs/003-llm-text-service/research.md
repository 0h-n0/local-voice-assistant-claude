# Research: LLM Text Response Service

**Feature**: 003-llm-text-service
**Date**: 2025-12-26

## Research Tasks

### 1. OpenAI Python SDK Integration

**Decision**: Use `openai` Python SDK v1.x with async client

**Rationale**:
- Official SDK with full async support (`AsyncOpenAI` client)
- Type hints and Pydantic compatibility
- Built-in retry logic and error handling
- Streaming support via `stream=True` parameter

**Alternatives Considered**:
- `httpx` direct API calls: More control but loses SDK benefits (retry, typing, updates)
- `litellm`: Abstraction layer for multiple providers, but adds complexity for single-provider use

**Implementation Notes**:
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = await client.chat.completions.create(
    model="gpt-4o-mini",  # or gpt-3.5-turbo as fallback
    messages=[...],
    max_tokens=1000,
)
```

### 2. Model Selection (gpt-5-mini)

**Decision**: Use `gpt-4o-mini` as primary model, with fallback to `gpt-3.5-turbo`

**Rationale**:
- `gpt-5-mini` does not exist as of 2025-01
- `gpt-4o-mini` is the current fast/cheap model from OpenAI (released 2024)
- Provides good Japanese language support
- Cost-effective for conversational use

**Alternatives Considered**:
- `gpt-4o`: Higher quality but significantly more expensive
- `gpt-3.5-turbo`: Older, but proven reliable as fallback
- `gpt-4-turbo`: Good balance but more expensive than 4o-mini

**Configuration**:
```python
# Environment variable for model override
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
```

### 3. Conversation Context Management

**Decision**: In-memory dict with conversation ID as key, automatic TTL cleanup

**Rationale**:
- Simplest solution for single-user local assistant
- No external dependencies (Redis, database)
- Conversation IDs generated client-side per spec clarification
- TTL prevents unbounded memory growth

**Implementation Pattern**:
```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

@dataclass
class Conversation:
    id: str
    messages: List[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class ConversationCache:
    def __init__(self, max_messages: int = 20, ttl_minutes: int = 60):
        self._cache: Dict[str, Conversation] = {}
        self._max_messages = max_messages
        self._ttl = timedelta(minutes=ttl_minutes)

    def get_or_create(self, conversation_id: str) -> Conversation:
        self._cleanup_expired()
        if conversation_id not in self._cache:
            self._cache[conversation_id] = Conversation(id=conversation_id)
        return self._cache[conversation_id]

    def _cleanup_expired(self) -> None:
        now = datetime.now()
        expired = [k for k, v in self._cache.items() if now - v.updated_at > self._ttl]
        for k in expired:
            del self._cache[k]
```

**Alternatives Considered**:
- Redis: Overkill for single-user, adds external dependency
- SQLite: Persistence not required per spec
- Session-based (no ID): Less control over conversation boundaries

### 4. System Prompt Design

**Decision**: Fixed Japanese assistant system prompt stored as constant

**Rationale**:
- Per spec clarification: fixed system prompt (not configurable)
- Japanese language focus as primary use case
- Helpful, concise assistant persona for voice interaction

**System Prompt**:
```python
SYSTEM_PROMPT = """あなたは日本語の音声アシスタントです。以下のガイドラインに従ってください：

1. 簡潔で自然な日本語で応答してください
2. 音声で読み上げることを考慮し、長すぎる回答は避けてください
3. 丁寧語（です・ます調）を使用してください
4. 質問に対して正確かつ役立つ情報を提供してください
5. 分からないことは正直に「分かりません」と答えてください

応答は音声合成で読み上げられることを想定し、箇条書きや記号の使用は最小限にしてください。"""
```

### 5. Error Handling and Retry Strategy

**Decision**: Use OpenAI SDK built-in retry with custom error mapping

**Rationale**:
- SDK provides automatic retry for transient errors (429, 500, 503)
- Map OpenAI exceptions to application-specific error codes
- Consistent error response format with existing STT API

**Error Mapping**:
| OpenAI Error | HTTP Status | Error Code |
|--------------|-------------|------------|
| `AuthenticationError` | 503 | `LLM_AUTH_ERROR` |
| `RateLimitError` | 503 | `LLM_RATE_LIMITED` |
| `APIConnectionError` | 503 | `LLM_CONNECTION_ERROR` |
| `APIStatusError` | 500 | `LLM_API_ERROR` |
| `BadRequestError` | 400 | `LLM_BAD_REQUEST` |

### 6. Concurrency Control

**Decision**: Use `asyncio.Semaphore` with configurable limit (default: 10)

**Rationale**:
- Prevents overwhelming OpenAI API with concurrent requests
- Matches pattern used in STT service
- Protects against rate limiting
- Allows queueing rather than immediate rejection

**Implementation**:
```python
class LLMService:
    def __init__(self, max_concurrent: int = 10):
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def generate_response(self, ...) -> str:
        async with self._semaphore:
            return await self._call_openai(...)
```

### 7. Input Validation

**Decision**: Validate at API layer with Pydantic, service layer enforces limits

**Rationale**:
- Pydantic models provide automatic validation and documentation
- 4000 character limit per spec requirement
- Reject empty messages at API layer

**Validation Rules**:
- Message content: 1-4000 characters
- Conversation ID: Required, non-empty string, max 64 characters
- Conversation history: Max 20 messages (truncate oldest if exceeded)

## Dependencies to Add

```toml
# pyproject.toml additions
dependencies = [
    # ... existing ...
    "openai>=1.12.0",
]
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key for authentication |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model to use for chat completions |
| `LLM_MAX_TOKENS` | No | `1000` | Maximum tokens in response |
| `LLM_MAX_CONCURRENT` | No | `10` | Maximum concurrent requests |
| `LLM_CONVERSATION_TTL_MINUTES` | No | `60` | Conversation cache TTL |
