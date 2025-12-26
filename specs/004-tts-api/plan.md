# Implementation Plan: TTS API (Text-to-Speech)

**Branch**: `004-tts-api` | **Date**: 2025-12-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-tts-api/spec.md`

## Summary

日本語テキストを自然な音声に変換する TTS (Text-to-Speech) API を実装する。Style-Bert-VITS2 を使用し、REST API エンドポイントを通じて音声合成サービスを提供する。話速パラメータのカスタマイズ、サービス健全性監視をサポートする。

## Technical Context

**Language/Version**: Python 3.11+ (Backend)
**Primary Dependencies**: FastAPI, Pydantic v2, Style-Bert-VITS2, torch, scipy
**Storage**: N/A (ステートレス処理、モデルはメモリに常駐)
**Testing**: pytest, pytest-asyncio, httpx
**Target Platform**: Linux server (GPU optional, CPU fallback)
**Project Type**: Web application (backend API)
**Performance Goals**: 100文字のテキストで10秒以内に音声生成
**Constraints**: 同時リクエスト数 1-3、メモリ使用量はモデルサイズ依存
**Scale/Scope**: 単一インスタンス、ローカル推論

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ⚠️ VIOLATION | Style-Bert-VITS2 はローカル推論だが、外部サーバーへのテキスト送信が発生しないことを確認必要 |
| II. Performance-Conscious | ✅ PASS | パフォーマンス目標定義済み（100文字/10秒） |
| III. Simplicity-First | ✅ PASS | 最小限の機能セット、単一話者のみ |
| IV. TDD | ✅ PASS | テスト先行開発を遵守 |
| V. Modular Architecture | ✅ PASS | TTS サービスは独立モジュールとして実装 |
| VI. Observability | ✅ PASS | 処理時間追跡、ステータスエンドポイント |
| VII. Language-Idiomatic | ✅ PASS | uv, pydantic, ruff, mypy strict 使用 |

### Privacy-First 詳細確認

Style-Bert-VITS2 は完全にローカルで動作するモデルであり、推論時にネットワーク通信は発生しない。モデルファイルは事前にローカルにダウンロードされ、すべての処理はオンデバイスで完結する。**PASS**

## Project Structure

### Documentation (this feature)

```text
specs/004-tts-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── tts.py           # TTS API endpoints
│   ├── models/
│   │   └── tts.py           # Pydantic models for TTS
│   ├── services/
│   │   └── tts_service.py   # TTS service with Style-Bert-VITS2
│   └── lib/
└── tests/
    ├── unit/
    │   └── test_tts_service.py
    ├── integration/
    │   └── test_tts_api.py
    └── contract/
        └── test_tts_contract.py
```

**Structure Decision**: 既存の backend/ 構造を継続使用。TTS 関連ファイルを api/, models/, services/ に追加。

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | - | - |

Constitution Check で重大な違反はなし。Privacy-First は確認済みで PASS。
