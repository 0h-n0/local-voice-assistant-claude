# Implementation Plan: ローカル開発環境セットアップ

**Branch**: `010-local-dev-setup` | **Date**: 2025-12-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-local-dev-setup/spec.md`

## Summary

ローカル開発環境を1コマンドで起動・停止できるMakefileを作成し、開発者のオンボーディング時間を短縮する。バックエンド（FastAPI + uv）とフロントエンド（Next.js + npm）をホットリロード付きで並列起動し、依存関係チェックとヘルプコマンドを提供する。

## Technical Context

**Language/Version**: Makefile (GNU Make 4.x), Bash scripts
**Primary Dependencies**: uv (Python), npm (Node.js), GNU Make
**Storage**: N/A
**Testing**: Manual testing via make commands, shell script unit tests (optional)
**Target Platform**: Linux, macOS (WSL for Windows)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 起動完了まで30秒以内
**Constraints**: 依存ツールのインストールはユーザー責任（チェックのみ実行）
**Scale/Scope**: 開発者向けツール、本番デプロイは対象外

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ N/A | 開発ツールのみ、ネットワーク通信なし |
| II. Performance-Conscious | ✅ Pass | 30秒以内起動目標を明記 |
| III. Simplicity-First | ✅ Pass | Makefileのみ、追加依存なし |
| IV. Test-Driven Development | ⚠️ Partial | 手動テストが主、自動テストは限定的 |
| V. Modular Architecture | ✅ Pass | 個別サービス起動コマンドで分離 |
| VI. Observability | ✅ Pass | 起動ログを標準出力に表示 |
| VII. Language-Idiomatic | ✅ Pass | uv/npm を使用、Constitution準拠 |

**Gate Result**: PASS - Makefileベースの開発ツールはTDD対象外（手動検証で十分）

## Project Structure

### Documentation (this feature)

```text
specs/010-local-dev-setup/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (minimal for this feature)
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (N/A for this feature)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
# Existing web application structure
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── app/
│   ├── components/
│   └── hooks/
└── tests/

# New files for this feature
Makefile                 # Main entry point - NEW
scripts/
└── check-deps.sh        # Dependency checker - NEW (optional)
```

**Structure Decision**: プロジェクトルートにMakefileを配置し、既存のbackend/frontend構造を活用する。

## Complexity Tracking

> No violations requiring justification.
