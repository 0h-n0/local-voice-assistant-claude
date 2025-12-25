# Data Model: STT API

**Feature**: 002-stt-api
**Date**: 2025-12-26

## Entities

### TranscriptionResponse

認識結果を表すレスポンスモデル。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | 認識されたテキスト全文 |
| duration_seconds | float | Yes | 音声ファイルの長さ（秒） |
| processing_time_seconds | float | Yes | 処理にかかった時間（秒） |
| segments | Segment[] | No | タイムスタンプ付きセグメント（利用可能な場合） |

**Validation Rules**:
- `text`: 空文字列を許可（無音の場合）
- `duration_seconds`: >= 0
- `processing_time_seconds`: >= 0

### Segment

テキストセグメント（タイムスタンプ付き）。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| text | string | Yes | セグメントのテキスト |
| start_time | float | Yes | 開始時間（秒） |
| end_time | float | Yes | 終了時間（秒） |

**Validation Rules**:
- `start_time`: >= 0
- `end_time`: > start_time

### STTStatus

STTサービスの状態を表すモデル。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| model_loaded | boolean | Yes | モデルがロード済みかどうか |
| model_name | string | Yes | モデル名（"reazonspeech-nemo-v2"） |
| device | string | Yes | 実行デバイス（"cuda" or "cpu"） |
| memory_usage_mb | float | Yes | 現在のメモリ使用量（MB） |

### StreamMessage

WebSocketストリーミング用メッセージ。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | enum | Yes | "partial", "final", "error" |
| text | string | Yes | 認識テキストまたはエラーメッセージ |
| is_final | boolean | Yes | 確定したセグメントかどうか |
| timestamp | float | No | メッセージのタイムスタンプ |

### ErrorResponse

エラーレスポンスモデル。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| error_code | string | Yes | エラーコード（例: "UNSUPPORTED_FORMAT"） |
| message | string | Yes | 人間可読なエラーメッセージ |
| details | object | No | 追加のエラー詳細 |

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNSUPPORTED_FORMAT | 400 | サポートされていないファイル形式 |
| FILE_TOO_LARGE | 413 | ファイルサイズが上限を超過（100MB） |
| EMPTY_AUDIO | 400 | 音声データが空または無効 |
| MODEL_NOT_LOADED | 503 | モデルがまだロードされていない |
| PROCESSING_ERROR | 500 | 音声処理中の内部エラー |

## Relationships

```
TranscriptionResponse
    └── segments: Segment[] (optional, 1:N)

StreamMessage (standalone, WebSocket only)

STTStatus (standalone, status endpoint only)

ErrorResponse (standalone, error cases only)
```

## State Transitions

### Model Loading State

```
[NOT_LOADED] ---(startup)---> [LOADING] ---(success)---> [LOADED]
                                  |
                                  └---(failure)---> [ERROR]
```

### Request Processing State

```
[RECEIVED] ---(validate)---> [PROCESSING] ---(success)---> [COMPLETED]
               |                  |
               └---(invalid)---> [REJECTED]
                                  |
                                  └---(error)---> [FAILED]
```

## Pydantic Model Examples

```python
from pydantic import BaseModel, Field
from typing import Literal

class Segment(BaseModel):
    text: str
    start_time: float = Field(ge=0)
    end_time: float

class TranscriptionResponse(BaseModel):
    text: str
    duration_seconds: float = Field(ge=0)
    processing_time_seconds: float = Field(ge=0)
    segments: list[Segment] | None = None

class STTStatus(BaseModel):
    model_loaded: bool
    model_name: str
    device: Literal["cuda", "cpu"]
    memory_usage_mb: float

class StreamMessage(BaseModel):
    type: Literal["partial", "final", "error"]
    text: str
    is_final: bool
    timestamp: float | None = None

class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: dict | None = None
```
