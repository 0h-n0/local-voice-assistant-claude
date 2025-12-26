# Implementation Plan: リアルタイム WebSocket 通信

**Branch**: `008-realtime-websocket` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-realtime-websocket/spec.md`

## Summary

WebSocket 通信を導入し、音声対話の各処理段階（音声入力中、文字起こし中、応答生成中、音声合成中）をリアルタイムでユーザーに表示する。外部ストリーミング STT サービスを使用してリアルタイム文字起こしを実現し、LLM ストリーミングレスポンスで応答テキストを逐次表示する。

## Technical Context

**Language/Version**: TypeScript 5.x (Frontend), Python 3.11+ (Backend)
**Primary Dependencies**:
- Backend: FastAPI WebSocket support, httpx (async HTTP for STT/LLM services), Pydantic v2
- Frontend: Native WebSocket API, React hooks for state management
**Storage**: N/A (ステートレス WebSocket 接続、セッション状態はメモリに保持)
**Testing**: Jest + React Testing Library (Frontend), pytest + pytest-asyncio (Backend)
**Target Platform**: Modern browsers with WebSocket support + local FastAPI server
**Project Type**: Web application (frontend + backend)
**Performance Goals**:
- 発話開始から最初の文字起こし表示まで < 1秒
- 処理状況の更新が各段階開始から < 500ms で画面に反映
- 接続切断から自動再接続完了まで平均 < 10秒
**Constraints**:
- 外部ストリーミング STT サービスへの依存（Privacy-First 原則の例外として明示的に許可）
- 認証なし（ローカル環境・シングルユーザー想定）
- 最大60秒の音声入力制限を維持
**Scale/Scope**: Single-user local assistant, 1 WebSocket connection per browser tab

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ⚠️ EXCEPTION | 外部ストリーミング STT サービスを使用（spec.md Assumptions で明示的に許可済み）。既存のローカル STT はバッチ処理用として維持 |
| II. Performance-Conscious | ✅ PASS | リアルタイム処理で体感遅延を削減。SC-001: <1秒で最初の文字起こし表示 |
| III. Simplicity-First | ✅ PASS | 既存 HTTP API との後方互換性維持（WebSocket 未対応環境でフォールバック） |
| IV. TDD | ✅ PASS | WebSocket メッセージハンドラーと状態管理のテストを先に作成 |
| V. Modular Architecture | ✅ PASS | WebSocket 通信層は既存の HTTP API と独立。イベントベースの疎結合設計 |
| VI. Observability | ✅ PASS | 接続状態の可視化、処理状況のリアルタイム表示 |
| VII. Language-Idiomatic | ✅ PASS | FastAPI WebSocket support、TypeScript strict mode、React hooks |

## Project Structure

### Documentation (this feature)

```text
specs/008-realtime-websocket/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── websocket.py       # NEW: WebSocket endpoint
│   │   └── ... (existing)
│   ├── models/
│   │   ├── websocket.py       # NEW: WebSocket message models
│   │   └── ... (existing)
│   ├── services/
│   │   ├── streaming_stt.py   # NEW: Streaming STT service adapter
│   │   ├── streaming_llm.py   # NEW: Streaming LLM service adapter
│   │   └── ... (existing)
│   └── lib/
│       └── websocket_manager.py  # NEW: WebSocket connection management
└── tests/
    ├── unit/
    │   ├── test_websocket_models.py
    │   └── test_streaming_services.py
    ├── integration/
    │   └── test_websocket_endpoint.py
    └── ... (existing)

frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── RealtimeTranscript.tsx    # NEW: リアルタイム文字起こし表示
│   │   │   ├── ProcessingStatus.tsx      # NEW: 処理状況インジケーター
│   │   │   └── ... (existing)
│   │   └── status/
│   │       └── ConnectionIndicator.tsx   # NEW: 接続状態表示
│   ├── hooks/
│   │   ├── useWebSocket.ts               # NEW: WebSocket接続管理
│   │   ├── useRealtimeTranscript.ts      # NEW: リアルタイム文字起こし状態
│   │   ├── useProcessingStatus.ts        # NEW: 処理状況状態管理
│   │   └── ... (existing)
│   ├── lib/
│   │   ├── websocket.ts                  # NEW: WebSocket クライアント
│   │   └── ... (existing)
│   └── types/
│       ├── websocket.ts                  # NEW: WebSocket メッセージ型定義
│       └── ... (existing)
└── tests/
    ├── components/
    │   ├── RealtimeTranscript.test.tsx
    │   ├── ProcessingStatus.test.tsx
    │   └── ConnectionIndicator.test.tsx
    ├── hooks/
    │   ├── useWebSocket.test.ts
    │   └── useRealtimeTranscript.test.ts
    └── lib/
        └── websocket.test.ts
```

**Structure Decision**: Web application with frontend/backend separation. Backend adds WebSocket endpoint alongside existing HTTP APIs. Frontend adds WebSocket hooks and real-time display components.

## Complexity Tracking

> **Constitution violation requiring justification**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Privacy-First exception (外部 STT サービス) | リアルタイム文字起こしにはストリーミング対応の STT が必要。既存のローカル STT (ReazonSpeech/NeMo) はバッチ処理のみ対応 | ローカルストリーミング STT (Whisper.cpp) は現時点でリアルタイム性能が不十分。将来的にローカル STT への移行を検討 |
