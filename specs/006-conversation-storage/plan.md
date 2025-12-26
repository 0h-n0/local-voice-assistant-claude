# Implementation Plan: Conversation History Storage

**Branch**: `006-conversation-storage` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-conversation-storage/spec.md`

## Summary

会話履歴ストレージ機能を実装する。SQLiteを使用してユーザーとアシスタントの会話履歴を保存・取得・削除できるようにする。音声対話オーケストレーター（005-voice-orchestrator）と統合し、対話完了時に自動的にメッセージを保存する。REST APIエンドポイントで履歴の取得・削除機能を提供する。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, Pydantic v2, aiosqlite（非同期SQLiteアクセス）
**Storage**: SQLite（ローカルファイルシステム）
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux/macOS（ローカル環境）
**Project Type**: Web application (backend-only for this feature)
**Performance Goals**: 保存100ms以内、取得500ms以内（100メッセージ）、一覧取得200ms以内
**Constraints**: 1,000会話・10,000メッセージ規模で性能劣化なし
**Scale/Scope**: シングルユーザー、ローカル使用

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ PASS | SQLiteローカル保存、外部通信なし |
| II. Performance-Conscious | ✅ PASS | 非同期DB操作、パフォーマンス目標定義済み |
| III. Simplicity-First | ✅ PASS | SQLite単一ファイル、シンプルなCRUD操作 |
| IV. TDD | ✅ PASS | テスト駆動で実装予定 |
| V. Modular Architecture | ✅ PASS | ConversationStorageServiceとして独立モジュール化 |
| VI. Observability | ✅ PASS | 構造化ログ出力予定 |
| VII. Python-Idiomatic | ✅ PASS | uv, pydantic, ruff使用 |

## Project Structure

### Documentation (this feature)

```text
specs/006-conversation-storage/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── conversations.py    # REST API endpoints
│   ├── models/
│   │   └── conversation.py     # Pydantic models
│   ├── services/
│   │   └── conversation_storage_service.py  # Storage service
│   └── db/
│       └── database.py         # SQLite connection management
└── tests/
    ├── unit/
    │   └── test_conversation_storage_service.py
    ├── integration/
    │   └── test_conversation_api.py
    └── contract/
        └── test_conversation_contract.py
```

**Structure Decision**: 既存のbackend構造に従い、api/, models/, services/にファイルを追加。新たにdb/ディレクトリを作成しデータベース接続管理を配置。

## Complexity Tracking

> No Constitution violations - no entries needed.
