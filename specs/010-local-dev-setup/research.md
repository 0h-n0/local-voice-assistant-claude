# Research: ローカル開発環境セットアップ

**Date**: 2025-12-27
**Feature**: 010-local-dev-setup

## Research Topics

### 1. Makefile による並列プロセス起動

**Decision**: GNU Make の `-j` オプションではなく、`&` によるバックグラウンド実行と `trap` によるシグナルハンドリングを使用

**Rationale**:
- `-j` は独立したターゲットの並列ビルド向けで、長時間実行プロセスには不向き
- `&` でバックグラウンド起動し、Ctrl+C で両プロセスを終了させる
- `trap` を使用してクリーンなシャットダウンを実現

**Alternatives Considered**:
- **foreman/honcho**: 追加依存が必要、シンプルさ原則に反する
- **docker-compose**: 本フェーズでは対象外（Assumptionsで明記）
- **シェルスクリプトのみ**: Makefileの方がコマンド一覧が分かりやすい

### 2. 依存関係チェックの実装方法

**Decision**: Makefile内で `command -v` を使用したインラインチェック

**Rationale**:
- 外部スクリプト不要でシンプル
- 失敗時に明確なエラーメッセージを表示可能
- 各コマンド実行前に必要な依存のみチェック

**Alternatives Considered**:
- **別ファイル（check-deps.sh）**: 管理すべきファイルが増える
- **Makefileのpre-requisite**: 毎回全チェックは冗長

### 3. ホットリロードの確保

**Decision**: 既存のコマンドをそのまま使用
- Backend: `uv run uvicorn src.main:app --reload`
- Frontend: `npm run dev`

**Rationale**:
- uvicornの`--reload`とNext.jsの`npm run dev`は標準でホットリロード対応
- 追加設定不要

**Alternatives Considered**:
- **watchdog等の外部ツール**: 不要、標準機能で十分

### 4. プロセス管理とシグナルハンドリング

**Decision**: `trap` を使用してSIGINT/SIGTERMをキャッチし、子プロセスをkill

**Rationale**:
- Ctrl+Cで全プロセスを確実に終了
- ポートが残留しない

**Pattern**:
```makefile
.PHONY: dev
dev:
	@trap 'kill 0' SIGINT SIGTERM EXIT; \
	$(MAKE) backend & \
	$(MAKE) frontend & \
	wait
```

### 5. ポート設定

**Decision**: 既存の設定を維持
- Backend: 8000 (FastAPI default)
- Frontend: 3000 (Next.js default)

**Rationale**:
- 既存コードベースとの一貫性
- 標準的なポート番号

## Summary

本機能はシンプルなMakefileで実装可能。追加の外部依存やパターンは不要。既存のuv/npm コマンドをラップするだけで目標を達成できる。
