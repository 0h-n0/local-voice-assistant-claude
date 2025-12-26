# Data Model: TTS API (Text-to-Speech)

**Date**: 2025-12-26
**Feature**: [spec.md](./spec.md) | [plan.md](./plan.md)

## Entity Definitions

### TTSSynthesisRequest

音声合成リクエスト。

```python
from pydantic import BaseModel, Field

class TTSSynthesisRequest(BaseModel):
    """TTS 音声合成リクエスト"""

    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="合成する日本語テキスト",
        examples=["こんにちは、音声アシスタントです。"],
    )

    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="話速スケール（0.5=遅い、1.0=通常、2.0=速い）",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "こんにちは",
                "speed": 1.0,
            }
        }
    )
```

### TTSSynthesisResponse

音声合成レスポンス（メタデータ）。実際の音声は `audio/wav` で返却。

```python
class TTSSynthesisResponse(BaseModel):
    """TTS 音声合成レスポンスメタデータ"""

    text: str = Field(
        ...,
        description="合成したテキスト",
    )

    audio_length_seconds: float = Field(
        ...,
        ge=0,
        description="生成された音声の長さ（秒）",
    )

    sample_rate: int = Field(
        ...,
        description="サンプリングレート（Hz）",
        examples=[44100],
    )

    processing_time_seconds: float = Field(
        ...,
        ge=0,
        description="処理時間（秒）",
    )
```

### TTSStatus

サービス状態。

```python
from enum import Enum
from datetime import datetime
from typing import Optional

class TTSHealthStatus(str, Enum):
    """TTS サービス健全性ステータス"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

class TTSStatus(BaseModel):
    """TTS サービス状態"""

    status: TTSHealthStatus = Field(
        ...,
        description="サービス健全性ステータス",
    )

    model_loaded: bool = Field(
        ...,
        description="TTS モデルがロードされているか",
    )

    model_name: Optional[str] = Field(
        default=None,
        description="ロードされているモデル名",
    )

    device: str = Field(
        ...,
        description="推論デバイス（cpu/cuda）",
    )

    last_check: datetime = Field(
        ...,
        description="最終ヘルスチェック時刻",
    )

    error_message: Optional[str] = Field(
        default=None,
        description="エラー詳細（status が healthy でない場合）",
    )
```

### TTSErrorResponse

エラーレスポンス。

```python
from enum import Enum

class TTSErrorCode(str, Enum):
    """TTS エラーコード"""
    EMPTY_TEXT = "EMPTY_TEXT"
    TEXT_TOO_LONG = "TEXT_TOO_LONG"
    INVALID_SPEED = "INVALID_SPEED"
    MODEL_NOT_LOADED = "MODEL_NOT_LOADED"
    SYNTHESIS_FAILED = "SYNTHESIS_FAILED"
    SERVICE_BUSY = "SERVICE_BUSY"

class TTSErrorResponse(BaseModel):
    """TTS エラーレスポンス"""

    error_code: TTSErrorCode = Field(
        ...,
        description="機械可読エラーコード",
    )

    message: str = Field(
        ...,
        description="人間可読エラーメッセージ",
    )

    details: Optional[dict] = Field(
        default=None,
        description="追加エラー情報",
    )
```

## Entity Relationships

```
┌──────────────────────┐
│ TTSSynthesisRequest  │
│   - text             │
│   - speed            │
└──────────┬───────────┘
           │
           │ POST /api/tts/synthesize
           ▼
┌──────────────────────┐     ┌──────────────────────┐
│   TTSService         │────▶│  WAV Audio Response  │
│   (processes)        │     │  (binary)            │
└──────────────────────┘     └──────────────────────┘
           │
           │ On error
           ▼
┌──────────────────────┐
│   TTSErrorResponse   │
│   - error_code       │
│   - message          │
└──────────────────────┘

┌──────────────────────┐
│     TTSStatus        │◀──── GET /api/tts/status
│   - status           │
│   - model_loaded     │
│   - device           │
└──────────────────────┘
```

## Validation Rules

| Field | Rule | Error Code |
|-------|------|------------|
| `text` | 1-5000 文字 | EMPTY_TEXT / TEXT_TOO_LONG |
| `text` | 空白のみ不可 | EMPTY_TEXT |
| `speed` | 0.5-2.0 | INVALID_SPEED |

## State Transitions

### TTSService Lifecycle

```
[Starting] ─────▶ [Loading Model] ─────▶ [Ready]
                        │                   │
                        │ Error             │ Unload
                        ▼                   ▼
                   [Failed]            [Stopped]
```

### Request Processing

```
[Received] ─▶ [Validating] ─▶ [Synthesizing] ─▶ [Complete]
                  │                  │
                  │ Invalid          │ Error
                  ▼                  ▼
              [Rejected]         [Failed]
```
