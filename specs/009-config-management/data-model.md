# Data Model: 設定管理機能

**Feature**: 009-config-management
**Date**: 2025-12-26

## Overview

設定管理機能のデータモデルを定義する。Pydantic Settings を使用し、型安全な設定管理を実現する。

## Entity Definitions

### 1. TTSSettings（TTS設定）

Text-to-Speech サービスに関する設定。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| model_path | Path | model_assets/jvnv-F1-jp | No | No | TTSモデルのディレクトリパス |
| device | str | cpu | No | No | 推論デバイス (cpu/cuda) |
| max_concurrent | int | 3 | No | No | 最大同時処理数 |
| model_file | str | jvnv-F1-jp_e160_s14000.safetensors | No | No | モデルファイル名 |
| config_file | str | config.json | No | No | 設定ファイル名 |
| style_vec_file | str | style_vectors.npy | No | No | スタイルベクトルファイル名 |
| bert_model | str | ku-nlp/deberta-v2-large-japanese-char-wwm | No | No | BERTモデル名 |
| max_text_length | int | 5000 | No | No | 最大テキスト長 |
| min_text_length | int | 1 | No | No | 最小テキスト長 |
| min_speed | float | 0.5 | No | No | 最小再生速度 |
| max_speed | float | 2.0 | No | No | 最大再生速度 |
| default_speed | float | 1.0 | No | No | デフォルト再生速度 |

**Environment Variables**: `TTS_MODEL_PATH`, `TTS_DEVICE`, `TTS_MAX_CONCURRENT`, etc.

### 2. OrchestratorSettings（オーケストレーター設定）

対話処理パイプラインのオーケストレーターに関する設定。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| max_concurrent | int | 5 | No | No | 最大同時処理数 |
| timeout | float | 30.0 | No | No | タイムアウト（秒） |
| semaphore_timeout | float | 2.0 | No | No | セマフォ取得タイムアウト（秒） |
| max_audio_duration | float | 300.0 | No | No | 最大音声長（秒） |
| min_audio_duration | float | 0.5 | No | No | 最小音声長（秒） |

**Environment Variables**: `ORCHESTRATOR_MAX_CONCURRENT`, `ORCHESTRATOR_TIMEOUT`, etc.

### 3. DeepgramSettings（Deepgram STT設定）

Deepgram 音声認識サービスに関する設定。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| api_key | SecretStr | "" | **Yes** | **Yes** | Deepgram API Key |
| model | str | nova-2 | No | No | STTモデル名 |
| language | str | ja | No | No | 認識言語 |
| sample_rate | int | 16000 | No | No | サンプリングレート |

**Environment Variables**: `DEEPGRAM_API_KEY`, `DEEPGRAM_MODEL`, `DEEPGRAM_LANGUAGE`, `DEEPGRAM_SAMPLE_RATE`

### 4. WebSocketSettings（WebSocket設定）

WebSocket リアルタイム通信に関する設定。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| heartbeat_interval | int | 30 | No | No | Ping間隔（秒） |
| max_audio_duration | int | 60 | No | No | 最大音声長（秒） |
| audio_chunk_interval | int | 100 | No | No | 音声チャンク間隔（ミリ秒） |

**Environment Variables**: `WS_HEARTBEAT_INTERVAL`, `WS_MAX_AUDIO_DURATION`, `WS_AUDIO_CHUNK_INTERVAL`

### 5. StorageSettings（ストレージ設定）

データ永続化に関する設定。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| conversation_db_path | str | data/conversations.db | No | No | 会話DBのパス |

**Environment Variables**: `CONVERSATION_DB_PATH`

### 6. OpenAISettings（OpenAI LLM設定）

OpenAI LLMサービスに関する設定（将来的に追加予定）。

| Field | Type | Default | Required | Secret | Description |
|-------|------|---------|----------|--------|-------------|
| api_key | SecretStr | "" | No | **Yes** | OpenAI API Key |
| model | str | gpt-4 | No | No | LLMモデル名 |
| base_url | AnyHttpUrl | https://api.openai.com/v1 | No | No | API Base URL |

**Environment Variables**: `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL`

### 7. Settings（ルート設定）

全設定を統合するルートモデル。

| Field | Type | Description |
|-------|------|-------------|
| tts | TTSSettings | TTS設定 |
| orchestrator | OrchestratorSettings | オーケストレーター設定 |
| deepgram | DeepgramSettings | Deepgram設定 |
| websocket | WebSocketSettings | WebSocket設定 |
| storage | StorageSettings | ストレージ設定 |
| openai | OpenAISettings | OpenAI設定 |
| log_level | str | ログレベル (DEBUG/INFO/WARNING/ERROR) |
| debug | bool | デバッグモード |

## Validation Rules

### Path Validation

- `model_path` は存在するディレクトリであること
- `conversation_db_path` の親ディレクトリが存在すること（または作成可能であること）

### Numeric Validation

- `max_concurrent` > 0
- `timeout` > 0
- `min_speed` < `max_speed`
- `min_text_length` < `max_text_length`
- `sample_rate` ∈ {8000, 16000, 22050, 44100, 48000}

### URL Validation

- `base_url` は有効なHTTP/HTTPS URLであること

### Secret Validation

- `api_key` は空文字でないこと（機能を使用する場合）

## Configuration Priority

1. **環境変数** (最優先)
2. `.env` ファイル
3. **デフォルト値** (最低優先)

## Response Model (API用)

### ConfigInfoResponse

設定確認APIのレスポンスモデル。機密情報はマスク済み。

| Field | Type | Description |
|-------|------|-------------|
| tts | dict | TTS設定（値をそのまま表示） |
| orchestrator | dict | オーケストレーター設定 |
| deepgram | dict | Deepgram設定（api_key は `**********`） |
| websocket | dict | WebSocket設定 |
| storage | dict | ストレージ設定 |
| openai | dict | OpenAI設定（api_key は `**********`） |
| log_level | str | ログレベル |
| debug | bool | デバッグモード |

## Relationships

```
Settings (root)
├── tts: TTSSettings
├── orchestrator: OrchestratorSettings
├── deepgram: DeepgramSettings
├── websocket: WebSocketSettings
├── storage: StorageSettings
└── openai: OpenAISettings
```

各サブ設定は独立しており、循環依存はない。
