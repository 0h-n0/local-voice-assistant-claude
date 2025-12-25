# Implementation Plan: STT API - Japanese Speech-to-Text

**Branch**: `002-stt-api` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-stt-api/spec.md`

## Summary

ReazonSpeech NeMo v2 モデルを使用した日本語音声認識APIを実装する。音声ファイルアップロード（P1）、リアルタイムWebSocketストリーミング（P2）、モデル状態確認（P3）の3つのエンドポイントを提供し、すべての処理をローカルで完結させる。

## Technical Context

**Language/Version**: Python 3.11+ (Backend)
**Primary Dependencies**: FastAPI, reazonspeech, NeMo, pydub (audio conversion), python-multipart (file upload)
**Storage**: N/A (ステートレス処理、モデルはメモリに常駐)
**Testing**: pytest with pytest-asyncio
**Target Platform**: Linux server with NVIDIA GPU (CPU fallback supported)
**Project Type**: Web application (backend extension)
**Performance Goals**: RTF < 0.5 (10秒の音声を5秒以内に処理)
**Constraints**: メモリ4GB以下、WebSocket遅延500ms以下
**Scale/Scope**: 同時10リクエスト対応

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ PASS | すべての処理はローカル完結、外部通信なし |
| II. Performance-Conscious | ✅ PASS | RTF < 0.5 目標、ストリーミング対応 |
| III. Simplicity-First | ✅ PASS | 最小限の依存関係、reazonspeechの公式APIを使用 |
| IV. TDD | ✅ PASS | contract/unit/integration テスト計画 |
| V. Modular Architecture | ✅ PASS | STTサービスは独立モジュールとして実装 |
| VI. Observability | ✅ PASS | 処理時間、メモリ使用量のメトリクス |
| VII. Language-Idiomatic | ✅ PASS | uv, pydantic, ruff, mypy strict |

## Project Structure

### Documentation (this feature)

```text
specs/002-stt-api/
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
│   │   ├── health.py        # 既存
│   │   └── stt.py            # 新規: STT APIエンドポイント
│   ├── models/
│   │   ├── health.py        # 既存
│   │   └── stt.py            # 新規: STT Pydanticモデル
│   ├── services/
│   │   └── stt_service.py    # 新規: STTビジネスロジック
│   └── main.py              # ルーター追加
└── tests/
    ├── contract/
    │   └── test_stt.py       # 新規: STT契約テスト
    ├── unit/
    │   └── test_stt_service.py  # 新規: STTサービステスト
    └── integration/
        └── test_stt_integration.py  # 新規: 統合テスト
```

**Structure Decision**: 既存のbackend構造を拡張。STT機能は `api/stt.py` + `services/stt_service.py` + `models/stt.py` として追加。Constitution V (Modular Architecture) に従い、独立してテスト可能な構成。

## Complexity Tracking

> No Constitution violations - no entries needed.
