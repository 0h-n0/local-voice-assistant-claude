# Implementation Plan: Voice Dialogue Orchestrator

**Branch**: `005-voice-orchestrator` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-voice-orchestrator/spec.md`

## Summary

音声入力から音声応答までの一連の処理（STT → LLM → TTS）を統合するオーケストレーターを実装する。単一のAPIエンドポイントで音声対話を完結させ、既存の各サービスを順次呼び出すパイプラインを構築する。レスポンスはWAV音声ファイルとして返却し、処理メタデータはHTTPヘッダーに含める。

## Technical Context

**Language/Version**: Python 3.11+ (Backend)
**Primary Dependencies**: FastAPI, Pydantic v2, httpx (内部サービス呼び出し用)
**Storage**: N/A（ステートレス処理、音声データは永続化しない）
**Testing**: pytest, pytest-asyncio
**Target Platform**: Linux server (Docker対応)
**Project Type**: web (backend only - 既存バックエンドに追加)
**Performance Goals**: 30秒以内に応答（10秒以内の音声入力の場合）、5件同時リクエスト処理
**Constraints**: 音声入力最大5分、同時リクエスト数制限、日本語のみ対応
**Scale/Scope**: 単一ターン対話、既存STT/LLM/TTS APIの統合

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | N/A | オーケストレーターは内部サービス呼び出しのみ。外部通信は既存サービスの責務 |
| II. Performance-Conscious | PASS | 30秒以内応答目標を設定、同時リクエスト制限で負荷管理 |
| III. Simplicity-First | PASS | 既存APIを順次呼び出すシンプルなパイプライン構成 |
| IV. Test-Driven Development | PASS | TDDアプローチ: テスト先行、モック使用で各サービスを独立テスト |
| V. Modular Architecture | PASS | orchestrator_service として独立モジュール化、既存サービスとの疎結合 |
| VI. Observability | PASS | 各ステップの処理時間をヘッダーで公開、構造化ログ出力 |
| VII. Language-Idiomatic | PASS | uv, Pydantic v2, ruff, mypy strict 使用 |

**Gate Status**: PASS - Phase 0 進行可

## Project Structure

### Documentation (this feature)

```text
specs/005-voice-orchestrator/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── openapi.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── orchestrator.py    # NEW: オーケストレーターエンドポイント
│   ├── models/
│   │   └── orchestrator.py    # NEW: リクエスト/レスポンスモデル
│   ├── services/
│   │   └── orchestrator_service.py  # NEW: パイプライン処理ロジック
│   ├── config.py              # MODIFY: オーケストレーター設定追加
│   ├── dependencies.py        # MODIFY: DI追加
│   └── main.py                # MODIFY: ルーター登録
└── tests/
    ├── contract/
    │   └── test_orchestrator_contract.py  # NEW
    ├── integration/
    │   └── test_orchestrator_api.py       # NEW
    └── unit/
        └── test_orchestrator_service.py   # NEW
```

**Structure Decision**: 既存のバックエンド構造（backend/src/）に新規モジュールを追加。STT/LLM/TTSと同じパターンを踏襲し、api/models/services の3層構成を維持。

## Complexity Tracking

> 特に Constitution 違反なし。シンプルなパイプライン構成を採用。

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |
