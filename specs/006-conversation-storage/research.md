# Research: Conversation History Storage

**Feature**: 006-conversation-storage
**Date**: 2025-12-26

## SQLite Async Library Selection

### Decision: aiosqlite

**Rationale**:
- FastAPIの非同期アーキテクチャと自然に統合
- SQLiteの軽量さを維持しつつ非同期I/Oを実現
- シンプルなAPI、学習コストが低い
- アクティブにメンテナンスされている

**Alternatives Considered**:
- `databases` + `aiosqlite`: より抽象的だが、SQLite単体には過剰
- `sqlalchemy[asyncio]`: ORMは本機能には過剰（シンプルなCRUD操作のみ）
- 同期的な`sqlite3`: FastAPIの非同期パターンに反する

## Database Schema Design

### Decision: 2テーブル構成（conversations, messages）

**Rationale**:
- 正規化により会話とメッセージを分離
- 会話単位での操作（削除、一覧取得）が効率的
- メッセージの順序はタイムスタンプで管理

**Schema**:
```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at DESC);
```

**Alternatives Considered**:
- 単一テーブル（JSONでメッセージ格納）: クエリ柔軟性が低下
- 複雑な正規化（separate roles table等）: 過剰な複雑さ

## Connection Pool Strategy

### Decision: シングルコネクションプール

**Rationale**:
- SQLiteはファイルベースで同時接続数に制限
- WALモードで並行読み取りをサポート
- ローカル使用のため複雑なプーリングは不要

**Implementation**:
- アプリケーション起動時にコネクション初期化
- WALモード有効化（`PRAGMA journal_mode=WAL`）
- 外部キー制約有効化（`PRAGMA foreign_keys=ON`）

## Orchestrator Integration Pattern

### Decision: サービス直接呼び出し

**Rationale**:
- 既存のオーケストレーターパターンと整合
- HTTPオーバーヘッドなし
- トランザクション境界が明確

**Implementation**:
- `ConversationStorageService`をオーケストレーターに注入
- `save_message(conversation_id, role, content)`メソッドを提供
- 新規会話の場合は自動的にconversationレコードを作成

## Error Handling Strategy

### Decision: 専用例外クラス + エラーコード

**Rationale**:
- 既存のOrchestratorErrorパターンと整合
- REST APIでの適切なHTTPステータスマッピング
- ログでの分類が容易

**Error Codes**:
- `CONVERSATION_NOT_FOUND`: 404
- `DATABASE_ERROR`: 503
- `MESSAGE_TOO_LONG`: 400

## Performance Optimization

### Decision: インデックス + ページネーション

**Rationale**:
- 会話一覧取得はupdated_atでソート → インデックス必須
- メッセージ取得はconversation_idでフィルタ → インデックス必須
- 大量データ対応のためoffset/limit方式

**Implementation**:
- 会話一覧: `ORDER BY updated_at DESC LIMIT ? OFFSET ?`
- メッセージ取得: `WHERE conversation_id = ? ORDER BY created_at ASC`
