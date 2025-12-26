# Quickstart: LLM Text Response Service

**Feature**: 003-llm-text-service
**Date**: 2025-12-26

## Prerequisites

- Python 3.11+
- Backend server running on `http://localhost:8000`
- OpenAI API key set in environment

## Configuration

Set required environment variables:

```bash
export OPENAI_API_KEY="sk-..."

# Optional configuration
export LLM_MODEL="gpt-4o-mini"           # Default: gpt-4o-mini
export LLM_MAX_TOKENS="1000"             # Default: 1000
export LLM_MAX_CONCURRENT="10"           # Default: 10
export LLM_CONVERSATION_TTL_MINUTES="60" # Default: 60
```

## Basic Usage

### 1. Send a Chat Message

Send a text message and receive a response:

```bash
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "こんにちは",
    "conversation_id": "my-session-001"
  }'
```

**Response**:

```json
{
  "text": "こんにちは！何かお手伝いできることはありますか？",
  "conversation_id": "my-session-001",
  "usage": {
    "prompt_tokens": 85,
    "completion_tokens": 18,
    "total_tokens": 103
  },
  "processing_time_seconds": 1.23
}
```

### 2. Continue a Conversation

Use the same `conversation_id` to maintain context:

```bash
# First message
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "私の名前は田中です",
    "conversation_id": "conv-abc123"
  }'

# Follow-up message (context is remembered)
curl -X POST http://localhost:8000/api/llm/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "私の名前は何ですか？",
    "conversation_id": "conv-abc123"
  }'
```

**Response** (includes context from previous message):

```json
{
  "text": "あなたのお名前は田中さんですね。",
  "conversation_id": "conv-abc123",
  "usage": {
    "prompt_tokens": 156,
    "completion_tokens": 12,
    "total_tokens": 168
  },
  "processing_time_seconds": 0.95
}
```

### 3. Clear a Conversation

Reset conversation history:

```bash
curl -X DELETE http://localhost:8000/api/llm/conversations/conv-abc123
```

**Response**:

```json
{
  "message": "Conversation cleared",
  "conversation_id": "conv-abc123"
}
```

### 4. Check Service Status

Verify LLM service is healthy:

```bash
curl http://localhost:8000/api/llm/status
```

**Response** (healthy):

```json
{
  "status": "healthy",
  "model": "gpt-4o-mini",
  "api_configured": true,
  "active_conversations": 3,
  "last_check": "2025-12-26T10:30:00Z"
}
```

**Response** (unhealthy - no API key):

```json
{
  "status": "unhealthy",
  "model": "gpt-4o-mini",
  "api_configured": false,
  "active_conversations": 0,
  "error_message": "OPENAI_API_KEY environment variable not set"
}
```

## Error Handling

The API returns structured error responses:

```json
{
  "error_code": "EMPTY_MESSAGE",
  "message": "Message content is empty or whitespace"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| EMPTY_MESSAGE | 400 | Message is empty or whitespace |
| MESSAGE_TOO_LONG | 400 | Message exceeds 4000 characters |
| INVALID_CONVERSATION_ID | 400 | Invalid conversation ID format |
| LLM_NOT_CONFIGURED | 503 | OpenAI API key not set |
| LLM_RATE_LIMITED | 503 | Rate limited by OpenAI |
| LLM_CONNECTION_ERROR | 503 | Cannot connect to OpenAI API |
| LLM_API_ERROR | 500 | OpenAI API returned error |
| LLM_PROCESSING_ERROR | 500 | Internal processing error |

## Python Client Example

```python
import requests
import uuid

BASE_URL = "http://localhost:8000/api/llm"

# Generate a conversation ID
conversation_id = f"session-{uuid.uuid4().hex[:8]}"

# Send a message
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "今日の予定を教えてください",
        "conversation_id": conversation_id
    }
)
result = response.json()
print(f"Response: {result['text']}")
print(f"Tokens used: {result['usage']['total_tokens']}")

# Continue conversation
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "message": "もう少し詳しく教えてください",
        "conversation_id": conversation_id
    }
)
print(f"Follow-up: {response.json()['text']}")

# Clear conversation when done
requests.delete(f"{BASE_URL}/conversations/{conversation_id}")

# Check service status
status = requests.get(f"{BASE_URL}/status").json()
print(f"Service status: {status['status']}")
```

## Conversation ID Guidelines

- Generate unique IDs client-side (UUID, timestamp-based, etc.)
- Use alphanumeric characters, hyphens, and underscores only
- Maximum length: 64 characters
- Conversations expire after 60 minutes of inactivity
- Maximum 20 messages per conversation (oldest trimmed)

## Performance Notes

- Response time depends on OpenAI API latency (typically 1-5 seconds)
- Maximum 10 concurrent requests (additional requests queue)
- First request may be slower (client initialization)
- Conversation history increases token usage and may slow responses
