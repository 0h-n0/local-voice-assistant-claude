# Data Model: Voice Dialogue Orchestrator

**Feature**: 005-voice-orchestrator
**Date**: 2025-12-26

## Overview

オーケストレーターAPIのリクエスト/レスポンスモデルとエラーモデルを定義する。

## Entities

### 1. VoiceDialogueRequest

音声対話リクエスト。マルチパートフォームデータとして受信。

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| audio | File (bytes) | Yes | max 100MB, 0.5s-5min duration | 入力音声ファイル |
| speed | float | No | 0.5 <= x <= 2.0, default: 1.0 | TTS話速スケール |

**Supported Audio Formats**: WAV, MP3, M4A, WebM, FLAC, OGG

---

### 2. VoiceDialogueResponse

音声対話レスポンス。音声ファイルとメタデータ。

| Field | Type | Location | Description |
|-------|------|----------|-------------|
| audio_data | bytes | Body | WAV形式音声データ |
| Content-Type | string | Header | `audio/wav` |
| X-Processing-Time-Total | float | Header | 総処理時間（秒） |
| X-Processing-Time-STT | float | Header | STT処理時間（秒） |
| X-Processing-Time-LLM | float | Header | LLM処理時間（秒） |
| X-Processing-Time-TTS | float | Header | TTS処理時間（秒） |
| X-Input-Duration | float | Header | 入力音声長（秒） |
| X-Input-Text-Length | int | Header | 認識テキスト文字数 |
| X-Output-Text-Length | int | Header | 応答テキスト文字数 |
| X-Output-Duration | float | Header | 出力音声長（秒） |
| X-Sample-Rate | int | Header | 出力サンプルレート |

---

### 3. ProcessingMetadata

内部処理メタデータ（ヘッダーに変換される）。

| Field | Type | Description |
|-------|------|-------------|
| total_time | float | 総処理時間（秒） |
| stt_time | float | STT処理時間（秒） |
| llm_time | float | LLM処理時間（秒） |
| tts_time | float | TTS処理時間（秒） |
| input_duration | float | 入力音声長（秒） |
| input_text_length | int | 認識テキスト文字数 |
| output_text_length | int | 応答テキスト文字数 |
| output_duration | float | 出力音声長（秒） |
| sample_rate | int | 出力サンプルレート |

---

### 4. OrchestratorErrorCode

エラーコード列挙型。

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_AUDIO_FORMAT | 400 | サポートされていない音声形式 |
| AUDIO_TOO_SHORT | 400 | 音声が短すぎる（0.5秒未満） |
| AUDIO_TOO_LONG | 400 | 音声が長すぎる（5分超過） |
| SPEECH_RECOGNITION_FAILED | 422 | 音声認識失敗（空テキスト） |
| STT_SERVICE_UNAVAILABLE | 503 | STTサービス利用不可 |
| LLM_SERVICE_UNAVAILABLE | 503 | LLMサービス利用不可 |
| LLM_RATE_LIMITED | 429 | LLM APIレート制限 |
| LLM_CONNECTION_ERROR | 503 | LLM API接続エラー |
| TTS_SERVICE_UNAVAILABLE | 503 | TTSサービス利用不可 |
| SYNTHESIS_FAILED | 500 | 音声合成失敗 |
| PROCESSING_TIMEOUT | 504 | 処理タイムアウト |
| TOO_MANY_REQUESTS | 429 | 同時リクエスト数超過 |

---

### 5. OrchestratorErrorResponse

エラーレスポンスモデル。

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| error_code | OrchestratorErrorCode | Yes | 機械可読エラーコード |
| message | string | Yes | 人間可読エラーメッセージ |
| details | dict | No | 追加エラー情報 |
| retry_after | int | No | リトライまでの秒数（429時） |

---

### 6. ServiceStatus

個別サービスステータス（STT/LLM/TTS共通の抽象）。

| Field | Type | Description |
|-------|------|-------------|
| status | HealthStatus | `healthy` / `degraded` / `unhealthy` |
| details | dict | サービス固有の詳細情報 |

---

### 7. OrchestratorStatus

オーケストレーター全体のステータス。

| Field | Type | Description |
|-------|------|-------------|
| status | HealthStatus | 全体ステータス |
| services | dict[str, ServiceStatus] | 各サービスのステータス |
| timestamp | datetime | チェック時刻 |

**ステータス判定ロジック**:
- `healthy`: 全サービスが healthy
- `degraded`: 一部が degraded だが動作可能
- `unhealthy`: いずれかが unhealthy（処理不可）

---

## Pydantic Models (Implementation Reference)

```python
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OrchestratorErrorCode(str, Enum):
    """Orchestrator error codes."""
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    AUDIO_TOO_SHORT = "AUDIO_TOO_SHORT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    SPEECH_RECOGNITION_FAILED = "SPEECH_RECOGNITION_FAILED"
    STT_SERVICE_UNAVAILABLE = "STT_SERVICE_UNAVAILABLE"
    LLM_SERVICE_UNAVAILABLE = "LLM_SERVICE_UNAVAILABLE"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"
    LLM_CONNECTION_ERROR = "LLM_CONNECTION_ERROR"
    TTS_SERVICE_UNAVAILABLE = "TTS_SERVICE_UNAVAILABLE"
    SYNTHESIS_FAILED = "SYNTHESIS_FAILED"
    PROCESSING_TIMEOUT = "PROCESSING_TIMEOUT"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"


class OrchestratorErrorResponse(BaseModel):
    """Orchestrator error response."""
    error_code: OrchestratorErrorCode
    message: str
    details: dict[str, Any] | None = None
    retry_after: int | None = None


class HealthStatus(str, Enum):
    """Health status enum."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ServiceStatus(BaseModel):
    """Individual service status."""
    status: HealthStatus
    details: dict[str, Any] = Field(default_factory=dict)


class OrchestratorStatus(BaseModel):
    """Orchestrator status response."""
    status: HealthStatus
    services: dict[str, ServiceStatus]
    timestamp: datetime


class ProcessingMetadata(BaseModel):
    """Processing metadata for response headers."""
    total_time: float
    stt_time: float
    llm_time: float
    tts_time: float
    input_duration: float
    input_text_length: int
    output_text_length: int
    output_duration: float
    sample_rate: int
```

---

## Validation Rules

### Audio File Validation

1. **Format**: 拡張子がサポート形式リストに含まれること
2. **Size**: ファイルサイズ <= 100MB
3. **Duration**: 0.5秒 <= 音声長 <= 300秒（5分）
4. **Content**: 空ファイルでないこと

### Speed Parameter Validation

1. **Range**: 0.5 <= speed <= 2.0
2. **Default**: 未指定時は 1.0

---

## State Transitions

オーケストレーターはステートレス設計のため、状態遷移なし。
各リクエストは独立して処理され、会話履歴は保持しない（単一ターン対話）。
