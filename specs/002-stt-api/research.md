# Research: STT API - Japanese Speech-to-Text

**Feature**: 002-stt-api
**Date**: 2025-12-26

## ReazonSpeech NeMo v2 Model

### Decision: reazonspeech-nemo-v2 を使用

**Rationale**:
- 35,000時間の日本語音声データで学習された高精度モデル
- 619Mパラメータの Fast Conformer アーキテクチャ
- 長時間音声（数時間）の推論をサポート
- Apache 2.0 ライセンスで商用利用可能
- 公式の `reazonspeech` ライブラリでシンプルなAPI提供

**Alternatives considered**:
- reazonspeech-espnet-v2: 118.85Mパラメータで軽量だが精度が低い
- reazonspeech-k2-v2: Next-gen Kaldiベースで異なるランタイム要件
- Whisper: 多言語対応だが日本語特化では ReazonSpeech が優位

### Model Usage

```python
from reazonspeech.nemo.asr import load_model, transcribe, audio_from_path

# Load audio file
audio = audio_from_path("speech.wav")

# Load model (singleton pattern recommended)
model = load_model()

# Transcribe
ret = transcribe(model, audio)
print(ret.text)
```

### Requirements

- NVIDIA NeMo framework
- CUDA対応GPU推奨（CPU fallback可能）
- 16kHzサンプリングレート

## Audio Processing

### Decision: pydub + soundfile を使用

**Rationale**:
- pydub: 多様なフォーマット（MP3, FLAC, OGG）からWAVへの変換
- soundfile: 高速なWAV読み込み、NumPy配列との相互変換
- librosa: リサンプリング（16kHzへの変換）に使用

**Alternatives considered**:
- ffmpeg直接呼び出し: pydubが内部で使用するため追加不要
- torchaudio: PyTorch依存が重い、NeMoで既に導入済み

### Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| WAV | .wav | ネイティブサポート |
| MP3 | .mp3 | pydubで変換 |
| FLAC | .flac | pydubで変換 |
| OGG | .ogg | pydubで変換 |

## WebSocket Streaming

### Decision: FastAPI WebSocket + チャンク処理

**Rationale**:
- FastAPIのネイティブWebSocketサポートを使用
- 音声チャンクを16kHz PCMで受信
- バッファリングして一定間隔または無音検出で transcribe

**Implementation Pattern**:

```python
@router.websocket("/api/stt/stream")
async def stream_transcribe(websocket: WebSocket):
    await websocket.accept()
    buffer = AudioBuffer()

    while True:
        chunk = await websocket.receive_bytes()
        buffer.add(chunk)

        if buffer.should_process():
            result = transcribe(model, buffer.get_audio())
            await websocket.send_json({
                "type": "partial" if buffer.is_continuing() else "final",
                "text": result.text
            })
```

**Alternatives considered**:
- gRPC streaming: 追加依存、FastAPIとの統合が複雑
- Server-Sent Events: 双方向通信に不向き

## Model Loading Strategy

### Decision: アプリケーション起動時にシングルトンでロード

**Rationale**:
- モデルロードに数十秒かかるため、リクエスト毎のロードは非現実的
- シングルトンパターンでメモリ効率化
- lifespan イベントで起動時ロード

**Implementation**:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

stt_service: STTService | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global stt_service
    stt_service = STTService()
    await stt_service.load_model()
    yield
    # Cleanup if needed

app = FastAPI(lifespan=lifespan)
```

**Alternatives considered**:
- Lazy loading: 初回リクエストで長時間待機が発生
- 別プロセス: IPC複雑化、Constitution III (Simplicity) 違反

## Concurrency Handling

### Decision: asyncio.Semaphore でリクエスト制限

**Rationale**:
- GPUメモリ制約により同時処理数を制限
- Semaphoreで最大同時処理数を管理
- キュー待ちのリクエストは待機または503エラー

**Implementation**:

```python
MAX_CONCURRENT_REQUESTS = 3
semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

async def transcribe_with_limit(audio):
    async with semaphore:
        return await stt_service.transcribe(audio)
```

## Error Handling

### Decision: 構造化エラーレスポンス

**Error Response Model**:

```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None

class ErrorCode(str, Enum):
    UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    EMPTY_AUDIO = "EMPTY_AUDIO"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    PROCESSING_ERROR = "PROCESSING_ERROR"
```

## Dependencies Summary

### Backend (pyproject.toml additions)

| Package | Version | Purpose |
|---------|---------|---------|
| reazonspeech | >=1.0.0 | NeMo ASR wrapper |
| pydub | >=0.25.0 | Audio format conversion |
| soundfile | >=0.12.0 | WAV file handling |
| python-multipart | >=0.0.6 | File upload support |
| websockets | >=12.0 | WebSocket support (FastAPI internal) |

### System Requirements

- NVIDIA GPU with CUDA 11.8+ (recommended)
- ffmpeg (for pydub audio conversion)
- ~4GB GPU memory for model

---

*Research completed - all technical decisions documented*
