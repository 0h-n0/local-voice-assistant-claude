# Quickstart: Conversation History Storage

**Feature**: 006-conversation-storage
**Date**: 2025-12-26

## Overview

会話履歴ストレージ機能の使用方法。音声対話オーケストレーターと統合されており、対話完了時に自動的にメッセージが保存される。REST APIで履歴の取得・削除が可能。

## Setup

### 1. Dependencies

```bash
cd backend
uv add aiosqlite
```

### 2. Database Initialization

データベースはアプリケーション起動時に自動的に初期化される。デフォルトのデータベースファイルパスは `data/conversations.db`。

環境変数で変更可能:
```bash
export CONVERSATION_DB_PATH=/path/to/conversations.db
```

## API Usage

### List Conversations

最新の会話一覧を取得:

```bash
curl http://localhost:8000/api/conversations
```

ページネーション付き:

```bash
curl "http://localhost:8000/api/conversations?limit=10&offset=20"
```

**Response**:
```json
{
  "conversations": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "message_count": 4,
      "created_at": "2025-12-26T10:00:00Z",
      "updated_at": "2025-12-26T10:05:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

### Get Conversation Detail

特定の会話の全メッセージを取得:

```bash
curl http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "今日の天気は？",
      "created_at": "2025-12-26T10:00:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "今日は晴れの予報です。",
      "created_at": "2025-12-26T10:00:05Z"
    }
  ],
  "created_at": "2025-12-26T10:00:00Z",
  "updated_at": "2025-12-26T10:00:05Z"
}
```

### Delete Conversation

会話を削除（関連メッセージも削除される）:

```bash
curl -X DELETE http://localhost:8000/api/conversations/550e8400-e29b-41d4-a716-446655440000
```

**Response**: `204 No Content`

## Error Handling

### 404 - Conversation Not Found

```json
{
  "error_code": "CONVERSATION_NOT_FOUND",
  "message": "Conversation with ID 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### 503 - Database Error

```json
{
  "error_code": "DATABASE_ERROR",
  "message": "Failed to connect to database"
}
```

## Orchestrator Integration

音声対話オーケストレーターでの使用例（内部呼び出し）:

```python
from src.services.conversation_storage_service import ConversationStorageService

# Orchestrator内での使用
async def process_dialogue(self, audio_data: bytes, ...):
    # STT → LLM → TTS処理
    ...

    # 会話履歴を自動保存
    await self._storage.save_message(
        conversation_id=conversation_id,
        role="user",
        content=recognized_text,
    )
    await self._storage.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
    )
```

## Performance Notes

- メッセージ保存: < 100ms
- 履歴取得（100メッセージ）: < 500ms
- 一覧取得（20件）: < 200ms
- 推奨規模: 1,000会話 / 10,000メッセージまで
