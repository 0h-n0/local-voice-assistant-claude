# Research: 設定管理機能

**Feature**: 009-config-management
**Date**: 2025-12-26

## Current State Analysis

### 既存の設定管理

現在 `backend/src/config.py` では以下の方式で設定を管理している：

```python
TTS_MODEL_PATH: Path = Path(os.getenv("TTS_MODEL_PATH", "model_assets/jvnv-F1-jp"))
TTS_DEVICE: str = os.getenv("TTS_DEVICE", "cpu")
```

**問題点**:
1. 型バリデーションがない（文字列からの手動変換）
2. 必須設定と任意設定の区別がない
3. 機密情報のマスキング機構がない
4. `.env` ファイルの自動読み込みがない
5. 設定一覧の確認手段がない

### 設定項目の洗い出し

現在のコードから抽出した設定項目：

| Category | Setting | Type | Default | Required |
|----------|---------|------|---------|----------|
| TTS | TTS_MODEL_PATH | Path | model_assets/jvnv-F1-jp | No |
| TTS | TTS_DEVICE | str | cpu | No |
| TTS | TTS_MAX_CONCURRENT | int | 3 | No |
| TTS | TTS_MODEL_FILE | str | jvnv-F1-jp_e160_s14000.safetensors | No |
| Orchestrator | ORCHESTRATOR_MAX_CONCURRENT | int | 5 | No |
| Orchestrator | ORCHESTRATOR_TIMEOUT | float | 30 | No |
| Orchestrator | ORCHESTRATOR_SEMAPHORE_TIMEOUT | float | 2.0 | No |
| Orchestrator | ORCHESTRATOR_MAX_AUDIO_DURATION | float | 300 | No |
| Orchestrator | ORCHESTRATOR_MIN_AUDIO_DURATION | float | 0.5 | No |
| Storage | CONVERSATION_DB_PATH | str | data/conversations.db | No |
| WebSocket | WS_HEARTBEAT_INTERVAL | int | 30 | No |
| WebSocket | WS_MAX_AUDIO_DURATION | int | 60 | No |
| WebSocket | WS_AUDIO_CHUNK_INTERVAL | int | 100 | No |
| Deepgram | DEEPGRAM_API_KEY | str (secret) | "" | **Yes** |
| Deepgram | DEEPGRAM_MODEL | str | nova-2 | No |
| Deepgram | DEEPGRAM_LANGUAGE | str | ja | No |
| Deepgram | DEEPGRAM_SAMPLE_RATE | int | 16000 | No |

## Technology Decisions

### Decision 1: pydantic-settings の採用

**Decision**: `pydantic-settings` を使用して設定管理を行う

**Rationale**:
- Pydantic v2 との完全な統合
- `.env` ファイルの自動読み込み
- 型バリデーションの自動実行
- `SecretStr` による機密情報のマスキング
- ネストされた設定モデルのサポート
- Constitution で Pydantic v2 が必須のため親和性が高い

**Alternatives Considered**:
- `python-dotenv` + 手動パース: シンプルだが型安全性が低い
- `dynaconf`: 高機能だが過剰、学習コストが高い
- `environ-config`: Pydantic との統合が弱い

### Decision 2: 設定のグループ化

**Decision**: 設定をカテゴリ別のネストされたモデルに分割

**Rationale**:
- 関連する設定をグループ化して見通しを良くする
- 各サービスが必要な設定のみを注入可能
- テスト時の部分的なモック化が容易

**Structure**:
```python
class Settings(BaseSettings):
    tts: TTSSettings
    orchestrator: OrchestratorSettings
    deepgram: DeepgramSettings
    websocket: WebSocketSettings
```

### Decision 3: 機密情報の取り扱い

**Decision**: `SecretStr` 型を使用し、ログ・レスポンスでは自動マスキング

**Rationale**:
- Pydantic 標準機能で追加実装不要
- `str()` 呼び出しで `**********` にマスクされる
- `.get_secret_value()` で明示的に値を取得

**Implementation**:
```python
class DeepgramSettings(BaseSettings):
    api_key: SecretStr = Field(default="", description="Deepgram API Key")
```

### Decision 4: バリデーションエラーのハンドリング

**Decision**: アプリケーション起動時に全設定をバリデーションし、失敗時は明確なエラーで停止

**Rationale**:
- 設定ミスは起動時に検出するべき
- ランタイムエラーより起動時エラーの方がデバッグしやすい
- FastAPI の lifespan で実装

### Decision 5: 設定確認 API

**Decision**: `/api/config` エンドポイントで現在の設定を表示（機密情報マスク済み）

**Rationale**:
- デバッグ時に便利
- Pydantic の `model_dump()` で自動マスキング
- 開発環境でのみ有効にするオプションも可能

## Best Practices Applied

### 1. 環境変数の命名規則

- プレフィックスなし（シンプルさ優先）
- アンダースコア区切り（UPPER_SNAKE_CASE）
- カテゴリはネストではなくフラット（`TTS_MODEL_PATH`）

### 2. デフォルト値の設計

- 開発環境で動作するデフォルト値を設定
- 必須設定（APIキー等）はデフォルトなしまたは空文字
- パスは相対パスをデフォルトにし、絶対パスも受け付ける

### 3. 設定ファイルの配置

- `backend/.env` - バックエンド用
- `frontend/.env.local` - フロントエンド用（Next.js 標準）
- `.env.example` - サンプル設定（リポジトリにコミット）

## Implementation Notes

### pydantic-settings の追加

```bash
cd backend && uv add pydantic-settings
```

### 設定の読み込み順序

1. デフォルト値（コード内で定義）
2. `.env` ファイル（存在する場合）
3. 環境変数（最優先）

### 既存コードとの互換性

既存の `config.py` のモジュールレベル変数を維持しつつ、新しい `Settings` クラスからエクスポートすることで後方互換性を確保：

```python
settings = Settings()
TTS_MODEL_PATH = settings.tts.model_path  # 互換性のためのエイリアス
```
