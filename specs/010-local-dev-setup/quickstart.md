# Quickstart: ローカル開発環境セットアップ

**Date**: 2025-12-27
**Feature**: 010-local-dev-setup

## Prerequisites

以下のツールがインストールされていることを確認してください：

| Tool | Version | Check Command |
|------|---------|---------------|
| Python | 3.11+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| uv | any | `uv --version` |
| npm | any | `npm --version` |
| GNU Make | 4.x | `make --version` |

## Quick Start

### 1. リポジトリをクローン

```bash
git clone <repository-url>
cd local-voice-assistant-claude
```

### 2. 環境変数を設定

```bash
cp backend/.env.example backend/.env
# 必要に応じて .env を編集
```

### 3. 開発サーバーを起動

```bash
make dev
```

これにより以下が起動します：
- **Backend**: http://localhost:8000 (FastAPI)
- **Frontend**: http://localhost:3000 (Next.js)

### 4. 開発サーバーを停止

Ctrl+C を押すか、別のターミナルで：

```bash
make down
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make dev` | 全サービスを起動（バックエンド + フロントエンド） |
| `make backend` | バックエンドのみ起動 |
| `make frontend` | フロントエンドのみ起動 |
| `make down` | 全サービスを停止 |
| `make help` | 利用可能なコマンド一覧を表示 |

## Troubleshooting

### ポートが使用中の場合

```bash
# 使用中のプロセスを確認
lsof -i :8000
lsof -i :3000

# プロセスを終了
kill -9 <PID>
```

### 依存関係エラー

```bash
# Pythonパッケージを再インストール
cd backend && uv sync

# Node.jsパッケージを再インストール
cd frontend && npm install
```

### .env が見つからない

```bash
cp backend/.env.example backend/.env
# 必要なAPIキーを設定
```

## Verification

起動成功の確認：

1. http://localhost:3000 にアクセス → UIが表示される
2. http://localhost:8000/health にアクセス → `{"status": "healthy"}` が返る
3. ソースコードを編集 → ホットリロードで反映される
