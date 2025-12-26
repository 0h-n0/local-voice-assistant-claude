# Research: Voice Dialogue Orchestrator

**Feature**: 005-voice-orchestrator
**Date**: 2025-12-26

## 1. 既存サービスインターフェースの調査

### 1.1 STT Service (`STTService`)

**ファイル**: `backend/src/services/stt_service.py`

**主要メソッド**:
- `transcribe(audio_data: bytes, filename: str) -> TranscriptionResponse`
  - 入力: 音声ファイルバイト、ファイル名（形式検出用）
  - 出力: `TranscriptionResponse` (text, duration_seconds, processing_time_seconds, segments)
- `validate_audio_format(filename: str, data: bytes) -> tuple[bool, str | None]`
  - サポート形式: WAV, MP3, FLAC, OGG
- `get_status() -> STTStatus`

**オーケストレーターでの利用パターン**:
```python
stt_service = get_stt_service()
result = await stt_service.transcribe(audio_bytes, filename)
recognized_text = result.text
```

**Decision**: STTServiceを直接依存注入で取得し、`transcribe`メソッドを呼び出す
**Rationale**: 既存のサービスインスタンスを再利用することでリソース効率が良い。HTTP経由ではなく直接呼び出しで遅延を最小化。

---

### 1.2 LLM Service (`LLMService`)

**ファイル**: `backend/src/services/llm_service.py`

**主要メソッド**:
- `generate_response(message: str, conversation_id: str) -> tuple[str, TokenUsage | None]`
  - 入力: ユーザーメッセージ、会話ID
  - 出力: (応答テキスト, トークン使用量)
- `get_status() -> LLMStatus`

**システムプロンプト**: 既にLLMServiceに日本語音声アシスタント用のプロンプトが定義済み

**オーケストレーターでの利用パターン**:
```python
llm_service = get_llm_service()
response_text, usage = await llm_service.generate_response(
    message=recognized_text,
    conversation_id=request_id  # 単一ターンなので一意のIDを生成
)
```

**Decision**: LLMServiceを直接依存注入で取得し、`generate_response`を呼び出す
**Rationale**: 既存の会話管理機能を利用しつつ、オーケストレーターでは単一ターン用に一意のconversation_idを生成

---

### 1.3 TTS Service (`TTSService`)

**ファイル**: `backend/src/services/tts_service.py`

**主要メソッド**:
- `synthesize(text: str, speed: float) -> tuple[int, NDArray[np.int16]]`
  - 入力: テキスト、話速（0.5-2.0）
  - 出力: (サンプルレート, 音声データ配列)
- `audio_to_wav_bytes(sample_rate: int, audio: NDArray) -> bytes`
  - 音声配列をWAVバイトに変換
- `get_status() -> TTSStatus`
- `is_ready: bool` プロパティ

**オーケストレーターでの利用パターン**:
```python
tts_service = get_tts_service()
sample_rate, audio = await tts_service.synthesize(response_text, speed=1.0)
wav_bytes = tts_service.audio_to_wav_bytes(sample_rate, audio)
```

**Decision**: TTSServiceを直接依存注入で取得し、`synthesize`と`audio_to_wav_bytes`を呼び出す
**Rationale**: 既存のモデルインスタンスを共有し、メモリ効率を維持

---

## 2. オーケストレーターパイプライン設計

### 2.1 パイプラインフロー

```
音声入力 (bytes)
    ↓
[1] STT: transcribe() → テキスト
    ↓
[2] LLM: generate_response() → 応答テキスト
    ↓
[3] TTS: synthesize() → 音声データ
    ↓
[4] WAV変換: audio_to_wav_bytes() → WAVバイト
    ↓
音声出力 (bytes) + ヘッダーメタデータ
```

**Decision**: 順次実行（非並列）
**Rationale**: 各ステップは前ステップの出力に依存するため並列化不可。シンプルな順次パイプラインが最適。
**Alternatives considered**:
- ストリーミングパイプライン: 実装複雑性が高く、スコープ外として明記済み

---

### 2.2 エラーハンドリング戦略

| ステップ | エラータイプ | HTTPステータス | エラーコード |
|---------|-------------|---------------|-------------|
| 入力検証 | 無効形式 | 400 | INVALID_AUDIO_FORMAT |
| 入力検証 | ファイルサイズ超過 | 400 | AUDIO_TOO_LONG |
| STT | 認識失敗（空テキスト） | 422 | SPEECH_RECOGNITION_FAILED |
| STT | モデル未ロード | 503 | STT_SERVICE_UNAVAILABLE |
| LLM | API設定なし | 503 | LLM_SERVICE_UNAVAILABLE |
| LLM | レート制限 | 429 | LLM_RATE_LIMITED |
| LLM | API接続エラー | 503 | LLM_CONNECTION_ERROR |
| TTS | モデル未ロード | 503 | TTS_SERVICE_UNAVAILABLE |
| TTS | 合成失敗 | 500 | SYNTHESIS_FAILED |
| 全般 | タイムアウト | 504 | PROCESSING_TIMEOUT |
| 全般 | 同時リクエスト超過 | 429 | TOO_MANY_REQUESTS |

**Decision**: 各ステップで固有のエラーコードを返し、クライアントが問題を特定できるようにする
**Rationale**: エラーの原因が明確になり、デバッグとリトライ戦略が立てやすくなる

---

### 2.3 レスポンスヘッダー設計

```
X-Processing-Time-Total: 5.234        # 総処理時間（秒）
X-Processing-Time-STT: 1.523          # STT処理時間
X-Processing-Time-LLM: 2.145          # LLM処理時間
X-Processing-Time-TTS: 1.566          # TTS処理時間
X-Input-Duration: 3.5                 # 入力音声長（秒）
X-Input-Text-Length: 24               # 認識テキスト文字数
X-Output-Text-Length: 156             # 応答テキスト文字数
X-Output-Duration: 8.2                # 出力音声長（秒）
X-Sample-Rate: 44100                  # サンプルレート
Content-Type: audio/wav
```

**Decision**: 処理メタデータはカスタムHTTPヘッダーで返却
**Rationale**: 既存TTS APIと一貫性があり、音声ファイルのContent-Typeを維持できる

---

### 2.4 同時リクエスト制御

**Decision**: asyncio.Semaphore で同時リクエスト数を制限（デフォルト: 5）
**Rationale**:
- 各サービス（STT, TTS）が既に個別のセマフォを持っているが、オーケストレーター全体でも制限が必要
- GPU/メモリリソースの競合を防ぎ、安定した応答時間を維持

**Configuration**:
```python
ORCHESTRATOR_MAX_CONCURRENT = int(os.getenv("ORCHESTRATOR_MAX_CONCURRENT", "5"))
```

---

## 3. 入力検証ルール

### 3.1 音声ファイル検証

| 項目 | 制限 | 備考 |
|------|------|------|
| 最大ファイルサイズ | 100MB | STTServiceの既存制限を流用 |
| 最大音声長 | 5分（300秒） | spec要件 |
| 最小音声長 | 0.5秒 | 認識精度の下限 |
| サポート形式 | WAV, MP3, M4A, WebM | M4A, WebMは追加対応 |

**Decision**: M4A, WebMをサポート形式に追加
**Rationale**: ブラウザ録音（MediaRecorder API）でよく使用される形式。pydubでの変換が可能。
**Implementation note**: STTServiceの`SUPPORTED_FORMATS`を参照しつつ、オーケストレーター側で追加形式を処理

---

## 4. ステータスエンドポイント設計

### 4.1 集約ステータス

```json
{
  "status": "healthy|degraded|unhealthy",
  "services": {
    "stt": {
      "status": "healthy",
      "model_loaded": true,
      "model_name": "reazonspeech-nemo-v2"
    },
    "llm": {
      "status": "healthy",
      "model": "gpt-4o-mini",
      "api_configured": true
    },
    "tts": {
      "status": "healthy",
      "model_loaded": true,
      "model_name": "jvnv-F1-jp"
    }
  },
  "timestamp": "2025-12-26T10:30:00Z"
}
```

**Decision**: 個別サービスステータスを集約し、全体ステータスを判定
**Rationale**: 運用者が一目で全サービスの状態を把握でき、問題サービスを特定しやすい

**全体ステータス判定ロジック**:
- `healthy`: 全サービスがhealthy
- `degraded`: 一部サービスがdegraded、全体として動作可能
- `unhealthy`: いずれかのサービスがunhealthy（処理不可）

---

## 5. 技術的決定サマリー

| 項目 | 決定 | 理由 |
|------|------|------|
| サービス呼び出し | 直接メソッド呼び出し（DI） | 低遅延、リソース共有 |
| パイプライン | 順次実行 | 依存関係あり、シンプル |
| エラーハンドリング | ステップ固有エラーコード | デバッグ容易性 |
| レスポンス形式 | WAV + ヘッダーメタデータ | 既存TTSとの一貫性 |
| 同時リクエスト | Semaphore(5) | リソース保護 |
| 追加音声形式 | M4A, WebM | ブラウザ互換性 |
