# Data Model: ローカル開発環境セットアップ

**Date**: 2025-12-27
**Feature**: 010-local-dev-setup

## Overview

本機能はMakefileベースの開発ツールであり、永続化するデータモデルは存在しない。

## Entities

### 1. Makefile Targets

| Target | Description | Dependencies |
|--------|-------------|--------------|
| `dev` | 全サービス起動 | backend, frontend |
| `backend` | バックエンドのみ起動 | uv, Python |
| `frontend` | フロントエンドのみ起動 | npm, Node.js |
| `down` | 全サービス停止 | - |
| `help` | コマンド一覧表示 | - |

### 2. 依存関係チェック項目

| Dependency | Check Command | Required Version |
|------------|---------------|------------------|
| Python | `python3 --version` | 3.11+ |
| Node.js | `node --version` | 18+ |
| uv | `uv --version` | any |
| npm | `npm --version` | any |
| make | `make --version` | GNU Make 4.x |

### 3. 環境変数

既存の `.env` ファイルを使用。本機能で新規追加する環境変数はなし。

## State Transitions

N/A - 状態管理は不要（各コマンドは独立して実行）

## Relationships

```text
Makefile
├── dev ──────┬──→ backend (parallel)
│             └──→ frontend (parallel)
├── backend ──→ uv run uvicorn
├── frontend ─→ npm run dev
├── down ─────→ kill processes
└── help ─────→ display targets
```
