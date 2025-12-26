# Data Model: Conversation History Storage

**Feature**: 006-conversation-storage
**Date**: 2025-12-26

## Entities

### Conversation

会話セッションを表すエンティティ。複数のメッセージを含む。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string (UUID) | PRIMARY KEY | オーケストレーターが生成した会話ID |
| created_at | datetime | NOT NULL | 会話開始日時 (UTC) |
| updated_at | datetime | NOT NULL | 最終更新日時 (UTC) |

**Validation Rules**:
- id: UUID形式、空でないこと
- created_at: 過去または現在の日時
- updated_at: created_at以降の日時

### Message

会話内の個別メッセージを表すエンティティ。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | integer | PRIMARY KEY, AUTO INCREMENT | メッセージID |
| conversation_id | string (UUID) | FOREIGN KEY, NOT NULL | 所属する会話のID |
| role | enum | NOT NULL, IN ('user', 'assistant') | 発話者ロール |
| content | string | NOT NULL, MAX 10000 chars | メッセージ内容 |
| created_at | datetime | NOT NULL | メッセージ作成日時 (UTC) |

**Validation Rules**:
- conversation_id: 存在するConversationを参照
- role: 'user' または 'assistant' のみ
- content: 1文字以上10,000文字以下

## Relationships

```
Conversation 1 ──────< Message
     │                    │
     │ id ───────────────┘ conversation_id
```

- 1つのConversationは0個以上のMessageを持つ（1:N）
- Messageは必ず1つのConversationに属する
- Conversationが削除されると関連するMessageも削除される（CASCADE）

## State Transitions

### Conversation Lifecycle

```
                    ┌─────────────────┐
                    │     [new]       │
                    └────────┬────────┘
                             │ save_message() with new conversation_id
                             ▼
                    ┌─────────────────┐
     save_message() │    [active]     │ save_message()
          ─────────►│                 │◄─────────
                    └────────┬────────┘
                             │ delete()
                             ▼
                    ┌─────────────────┐
                    │   [deleted]     │
                    └─────────────────┘
```

## Pydantic Models

### Request/Response Models

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class MessageCreate(BaseModel):
    """Internal model for creating messages (from orchestrator)"""
    conversation_id: str
    role: MessageRole
    content: str = Field(..., min_length=1, max_length=10000)

class MessageResponse(BaseModel):
    """Message in API response"""
    id: int
    role: MessageRole
    content: str
    created_at: datetime

class ConversationSummary(BaseModel):
    """Conversation in list response"""
    id: str
    message_count: int
    created_at: datetime
    updated_at: datetime

class ConversationDetail(BaseModel):
    """Full conversation with messages"""
    id: str
    messages: list[MessageResponse]
    created_at: datetime
    updated_at: datetime

class ConversationListResponse(BaseModel):
    """Paginated conversation list"""
    conversations: list[ConversationSummary]
    total: int
    limit: int
    offset: int
```

### Error Models

```python
class ConversationErrorCode(str, Enum):
    CONVERSATION_NOT_FOUND = "CONVERSATION_NOT_FOUND"
    MESSAGE_TOO_LONG = "MESSAGE_TOO_LONG"
    DATABASE_ERROR = "DATABASE_ERROR"

class ConversationErrorResponse(BaseModel):
    error_code: ConversationErrorCode
    message: str
    details: dict[str, Any] | None = None
```

## Indexes

| Table | Index Name | Columns | Purpose |
|-------|------------|---------|---------|
| messages | idx_messages_conversation_id | conversation_id | 会話のメッセージ取得高速化 |
| conversations | idx_conversations_updated_at | updated_at DESC | 一覧取得のソート高速化 |
