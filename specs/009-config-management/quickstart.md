# Quickstart: 設定管理機能

**Feature**: 009-config-management
**Date**: 2025-12-26

## Prerequisites

- Python 3.11+
- uv (パッケージマネージャー)
- Node.js 18+ (フロントエンド用)

## Setup

### 1. 依存関係のインストール

```bash
# バックエンド
cd backend
uv add pydantic-settings

# フロントエンド（設定変更なし）
cd frontend
npm install
```

### 2. 設定ファイルの作成

```bash
# ルートディレクトリで
cp backend/.env.example backend/.env

# 必要な値を編集
vim backend/.env
```

### 3. 必須設定

最低限必要な設定項目：

```env
# Deepgram API Key（音声認識に必須）
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# OpenAI API Key（LLMに必須）
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. オプション設定

環境に応じてカスタマイズ可能な設定：

```env
# TTS設定
TTS_MODEL_PATH=model_assets/jvnv-F1-jp
TTS_DEVICE=cpu  # または cuda

# パフォーマンス設定
ORCHESTRATOR_MAX_CONCURRENT=5
ORCHESTRATOR_TIMEOUT=30

# ログ設定
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
DEBUG=false
```

## Verification

### 設定の確認

```bash
# バックエンドを起動
cd backend
uv run uvicorn src.main:app --reload

# 別ターミナルで設定確認API呼び出し
curl http://localhost:8000/api/config | jq
```

期待される出力（機密情報はマスク済み）：

```json
{
  "tts": {
    "model_path": "model_assets/jvnv-F1-jp",
    "device": "cpu",
    "max_concurrent": 3
  },
  "deepgram": {
    "api_key": "**********",
    "model": "nova-2",
    "language": "ja"
  },
  "openai": {
    "api_key": "**********",
    "model": "gpt-4"
  },
  "log_level": "INFO",
  "debug": false
}
```

### バリデーションエラーの確認

無効な設定を試す：

```bash
# 無効な値を設定
export TTS_MAX_CONCURRENT=-1

# アプリケーション起動
uv run uvicorn src.main:app --reload
# → ValidationError: TTS_MAX_CONCURRENT must be >= 1
```

## Manual Testing Checklist

### US1: 環境変数による設定管理

- [ ] `.env` ファイルに設定を記述し、アプリケーションが読み込むことを確認
- [ ] 環境変数が `.env` ファイルより優先されることを確認
- [ ] `.env` ファイルがなくてもデフォルト値で起動することを確認
- [ ] 無効な値（型エラー、範囲外）でバリデーションエラーが出ることを確認

### US2: モデルパスの設定

- [ ] `TTS_MODEL_PATH` を変更し、指定パスのモデルが使用されることを確認
- [ ] 存在しないパスを指定した場合、適切なエラーメッセージが出ることを確認

### US3: サービスURL設定

- [ ] サービスURLを変更し、正しいエンドポイントに接続することを確認
- [ ] 無効なURLを指定した場合、バリデーションエラーが出ることを確認

### US4: 設定の一覧表示

- [ ] `GET /api/config` で現在の設定が取得できることを確認
- [ ] APIキーなどの機密情報がマスクされていることを確認
- [ ] ログに機密情報が出力されていないことを確認

## Troubleshooting

### ValidationError: xxx

設定値がバリデーションに失敗しています。エラーメッセージを確認し、以下を確認してください：

- 型が正しいか（数値に文字列を入れていないか）
- 範囲が正しいか（負の値、ゼロなど）
- パスが存在するか

### 設定が反映されない

1. `.env` ファイルのパスが正しいか確認
2. 環境変数が既に設定されていないか確認（環境変数が優先）
3. アプリケーションを再起動

### APIキーがマスクされない

`SecretStr` 型が正しく適用されているか確認。`model_dump()` を使用してシリアライズすること。

## Next Steps

実装完了後：

1. `uv run pytest` でテスト実行
2. `uv run ruff check .` でリントチェック
3. `uv run mypy --strict src/` で型チェック
