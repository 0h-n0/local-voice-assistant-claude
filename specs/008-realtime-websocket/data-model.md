# Data Model: リアルタイム WebSocket 通信

**Feature**: 008-realtime-websocket
**Date**: 2025-12-27

## Overview

This document defines the WebSocket message types, state models, and data structures for real-time bidirectional communication between frontend and backend.

## WebSocket Message Types

### Server → Client Messages

```typescript
/**
 * All possible server-to-client message types.
 */
export type ServerMessage =
  | TranscriptPartialMessage
  | TranscriptFinalMessage
  | StatusUpdateMessage
  | ResponseChunkMessage
  | ResponseCompleteMessage
  | ErrorMessage
  | ConnectionAckMessage
  | PingMessage;

/**
 * Partial transcript during speech recognition.
 * Sent continuously while user is speaking.
 */
export interface TranscriptPartialMessage {
  type: "transcript_partial";
  content: string;
  confidence?: number; // 0.0-1.0
  timestamp: string;   // ISO 8601
}

/**
 * Final transcript after speech recognition completes.
 * Replaces all partial transcripts.
 */
export interface TranscriptFinalMessage {
  type: "transcript_final";
  content: string;
  confidence: number;  // 0.0-1.0
  duration_ms: number; // Audio duration in milliseconds
  timestamp: string;   // ISO 8601
}

/**
 * Processing status update.
 * Sent when transitioning between processing stages.
 */
export interface StatusUpdateMessage {
  type: "status_update";
  status: ProcessingStatus;
  timestamp: string; // ISO 8601
}

/**
 * LLM response chunk during streaming.
 * Content is accumulated on client side.
 */
export interface ResponseChunkMessage {
  type: "response_chunk";
  content: string; // Incremental text chunk
  chunk_index: number;
  timestamp: string; // ISO 8601
}

/**
 * Response complete notification.
 * Includes full text for verification and audio URL for TTS.
 */
export interface ResponseCompleteMessage {
  type: "response_complete";
  full_text: string;
  audio_available: boolean;
  timestamp: string; // ISO 8601
}

/**
 * Error notification.
 */
export interface ErrorMessage {
  type: "error";
  code: WebSocketErrorCode;
  message: string;
  details?: Record<string, unknown>;
  recoverable: boolean; // Can client retry?
  timestamp: string;    // ISO 8601
}

/**
 * Connection acknowledgement after successful handshake.
 */
export interface ConnectionAckMessage {
  type: "connection_ack";
  session_id: string;
  server_time: string; // ISO 8601
}

/**
 * Server ping for keepalive.
 */
export interface PingMessage {
  type: "ping";
  timestamp: string; // ISO 8601
}
```

### Client → Server Messages

```typescript
/**
 * All possible client-to-server message types.
 */
export type ClientMessage =
  | AudioChunkMessage
  | AudioEndMessage
  | TextInputMessage
  | CancelMessage
  | PongMessage;

/**
 * Audio chunk during voice recording.
 * Sent continuously while recording is active.
 */
export interface AudioChunkMessage {
  type: "audio_chunk";
  data: string;         // Base64 encoded audio data
  chunk_index: number;  // Sequential chunk number
  sample_rate: number;  // e.g., 16000
  format: AudioFormat;  // Audio encoding format
}

/**
 * Signal that audio stream has ended.
 * Triggers final STT processing.
 */
export interface AudioEndMessage {
  type: "audio_end";
  total_chunks: number;
  total_duration_ms: number;
}

/**
 * Text input (alternative to voice).
 */
export interface TextInputMessage {
  type: "text_input";
  content: string;
  conversation_id?: string; // Optional: continue existing conversation
}

/**
 * Cancel current operation.
 */
export interface CancelMessage {
  type: "cancel";
  reason?: string;
}

/**
 * Response to server ping.
 */
export interface PongMessage {
  type: "pong";
  timestamp: string; // Echo server timestamp
}

/**
 * Supported audio formats for streaming.
 */
export type AudioFormat = "pcm16" | "opus" | "webm";
```

## State Enums

### Processing Status

```typescript
/**
 * Processing pipeline stages.
 * Displayed to user as status indicator.
 */
export type ProcessingStatus =
  | "idle"        // Waiting for user input
  | "recording"   // User is speaking
  | "transcribing" // STT processing
  | "generating"  // LLM generating response
  | "synthesizing" // TTS processing
  | "playing"     // Audio playback
  | "error";      // Error state
```

### Connection Status

```typescript
/**
 * WebSocket connection status.
 * Displayed as connection indicator.
 */
export type ConnectionStatus =
  | "connecting"    // Initial connection attempt
  | "connected"     // Active connection
  | "reconnecting"  // Attempting to reconnect
  | "disconnected"  // No connection
  | "error";        // Connection error
```

### Error Codes

```typescript
/**
 * WebSocket-specific error codes.
 */
export type WebSocketErrorCode =
  // Connection errors
  | "CONNECTION_FAILED"
  | "CONNECTION_TIMEOUT"
  | "CONNECTION_CLOSED"
  // STT errors
  | "STT_SERVICE_ERROR"
  | "STT_TIMEOUT"
  | "AUDIO_TOO_SHORT"
  | "AUDIO_TOO_LONG"
  | "INVALID_AUDIO_FORMAT"
  // LLM errors
  | "LLM_SERVICE_ERROR"
  | "LLM_TIMEOUT"
  | "LLM_RATE_LIMITED"
  // TTS errors
  | "TTS_SERVICE_ERROR"
  | "TTS_TIMEOUT"
  // General errors
  | "INVALID_MESSAGE"
  | "INTERNAL_ERROR";
```

## Backend Pydantic Models

### WebSocket Message Models

```python
from enum import Enum
from typing import Literal, Union
from pydantic import BaseModel, Field
from datetime import datetime


class ProcessingStatus(str, Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    GENERATING = "generating"
    SYNTHESIZING = "synthesizing"
    PLAYING = "playing"
    ERROR = "error"


class WebSocketErrorCode(str, Enum):
    CONNECTION_FAILED = "CONNECTION_FAILED"
    CONNECTION_TIMEOUT = "CONNECTION_TIMEOUT"
    CONNECTION_CLOSED = "CONNECTION_CLOSED"
    STT_SERVICE_ERROR = "STT_SERVICE_ERROR"
    STT_TIMEOUT = "STT_TIMEOUT"
    AUDIO_TOO_SHORT = "AUDIO_TOO_SHORT"
    AUDIO_TOO_LONG = "AUDIO_TOO_LONG"
    INVALID_AUDIO_FORMAT = "INVALID_AUDIO_FORMAT"
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"
    LLM_TIMEOUT = "LLM_TIMEOUT"
    LLM_RATE_LIMITED = "LLM_RATE_LIMITED"
    TTS_SERVICE_ERROR = "TTS_SERVICE_ERROR"
    TTS_TIMEOUT = "TTS_TIMEOUT"
    INVALID_MESSAGE = "INVALID_MESSAGE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class AudioFormat(str, Enum):
    PCM16 = "pcm16"
    OPUS = "opus"
    WEBM = "webm"


# Server -> Client Messages

class TranscriptPartialMessage(BaseModel):
    type: Literal["transcript_partial"] = "transcript_partial"
    content: str
    confidence: float | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranscriptFinalMessage(BaseModel):
    type: Literal["transcript_final"] = "transcript_final"
    content: str
    confidence: float
    duration_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StatusUpdateMessage(BaseModel):
    type: Literal["status_update"] = "status_update"
    status: ProcessingStatus
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseChunkMessage(BaseModel):
    type: Literal["response_chunk"] = "response_chunk"
    content: str
    chunk_index: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ResponseCompleteMessage(BaseModel):
    type: Literal["response_complete"] = "response_complete"
    full_text: str
    audio_available: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorMessage(BaseModel):
    type: Literal["error"] = "error"
    code: WebSocketErrorCode
    message: str
    details: dict | None = None
    recoverable: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConnectionAckMessage(BaseModel):
    type: Literal["connection_ack"] = "connection_ack"
    session_id: str
    server_time: datetime = Field(default_factory=datetime.utcnow)


class PingMessage(BaseModel):
    type: Literal["ping"] = "ping"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


ServerMessage = Union[
    TranscriptPartialMessage,
    TranscriptFinalMessage,
    StatusUpdateMessage,
    ResponseChunkMessage,
    ResponseCompleteMessage,
    ErrorMessage,
    ConnectionAckMessage,
    PingMessage,
]


# Client -> Server Messages

class AudioChunkMessage(BaseModel):
    type: Literal["audio_chunk"] = "audio_chunk"
    data: str  # Base64 encoded
    chunk_index: int
    sample_rate: int = 16000
    format: AudioFormat = AudioFormat.PCM16


class AudioEndMessage(BaseModel):
    type: Literal["audio_end"] = "audio_end"
    total_chunks: int
    total_duration_ms: int


class TextInputMessage(BaseModel):
    type: Literal["text_input"] = "text_input"
    content: str
    conversation_id: str | None = None


class CancelMessage(BaseModel):
    type: Literal["cancel"] = "cancel"
    reason: str | None = None


class PongMessage(BaseModel):
    type: Literal["pong"] = "pong"
    timestamp: datetime


ClientMessage = Union[
    AudioChunkMessage,
    AudioEndMessage,
    TextInputMessage,
    CancelMessage,
    PongMessage,
]
```

## Frontend State Types

### WebSocket Connection State

```typescript
/**
 * WebSocket connection state managed by useWebSocket hook.
 */
export interface WebSocketState {
  /** Current connection status */
  status: ConnectionStatus;

  /** Session ID assigned by server */
  sessionId: string | null;

  /** Number of reconnection attempts */
  reconnectAttempts: number;

  /** Error message if connection failed */
  error: string | null;

  /** Last message timestamp for heartbeat monitoring */
  lastMessageAt: Date | null;
}

/**
 * WebSocket state actions.
 */
export type WebSocketAction =
  | { type: "CONNECTING" }
  | { type: "CONNECTED"; payload: { sessionId: string } }
  | { type: "DISCONNECTED" }
  | { type: "RECONNECTING"; payload: { attempt: number } }
  | { type: "ERROR"; payload: { error: string } }
  | { type: "MESSAGE_RECEIVED" };
```

### Real-time Transcript State

```typescript
/**
 * Real-time transcript state managed by useRealtimeTranscript hook.
 */
export interface RealtimeTranscriptState {
  /** Current partial transcript (updating in real-time) */
  partialTranscript: string;

  /** Final confirmed transcript */
  finalTranscript: string | null;

  /** Whether transcript is being updated */
  isTranscribing: boolean;

  /** Confidence score (0.0-1.0) */
  confidence: number | null;
}

/**
 * Transcript state actions.
 */
export type TranscriptAction =
  | { type: "PARTIAL_UPDATE"; payload: string }
  | { type: "FINAL_UPDATE"; payload: { text: string; confidence: number } }
  | { type: "CLEAR" };
```

### Processing Status State

```typescript
/**
 * Processing status state managed by useProcessingStatus hook.
 */
export interface ProcessingStatusState {
  /** Current processing stage */
  status: ProcessingStatus;

  /** Accumulated response text during streaming */
  streamingResponse: string;

  /** Response complete flag */
  isComplete: boolean;

  /** Error during processing */
  error: { code: WebSocketErrorCode; message: string } | null;
}

/**
 * Processing status actions.
 */
export type ProcessingStatusAction =
  | { type: "SET_STATUS"; payload: ProcessingStatus }
  | { type: "APPEND_RESPONSE"; payload: string }
  | { type: "COMPLETE"; payload: string }
  | { type: "ERROR"; payload: { code: WebSocketErrorCode; message: string } }
  | { type: "RESET" };
```

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Frontend State                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                                                        │
│  │  useWebSocket   │                                                        │
│  │                 │                                                        │
│  │ - status        │◄──── ConnectionIndicator (UI)                         │
│  │ - sessionId     │                                                        │
│  │ - reconnects    │                                                        │
│  └────────┬────────┘                                                        │
│           │                                                                 │
│           │ dispatch messages                                               │
│           ▼                                                                 │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐       │
│  │useRealtime      │   │useProcessing    │   │ useAudioPlayer      │       │
│  │Transcript       │   │Status           │   │ (existing)          │       │
│  │                 │   │                 │   │                     │       │
│  │- partialText    │   │- status         │   │- playback state     │       │
│  │- finalText      │   │- streaming      │   │- audio control      │       │
│  │- confidence     │   │- isComplete     │   │                     │       │
│  └────────┬────────┘   └────────┬────────┘   └──────────┬──────────┘       │
│           │                     │                       │                   │
│           ▼                     ▼                       ▼                   │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────────┐       │
│  │RealtimeTranscript│   │ProcessingStatus │   │  AudioPlayer        │       │
│  │(UI Component)   │   │(UI Component)   │   │  (existing)         │       │
│  └─────────────────┘   └─────────────────┘   └─────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ WebSocket Connection
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Backend                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     WebSocket Endpoint                               │   │
│  │                     /ws/realtime                                     │   │
│  └───────────┬─────────────────────┬─────────────────────┬─────────────┘   │
│              │                     │                     │                  │
│              ▼                     ▼                     ▼                  │
│  ┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐         │
│  │ Streaming STT     │ │ Streaming LLM     │ │  TTS Service      │         │
│  │ (Deepgram)        │ │ (OpenAI)          │ │  (existing)       │         │
│  │                   │ │                   │ │                   │         │
│  │ → transcript_     │ │ → response_chunk  │ │ → response_       │         │
│  │   partial         │ │                   │ │   complete        │         │
│  │ → transcript_     │ │                   │ │   (audio_url)     │         │
│  │   final           │ │                   │ │                   │         │
│  └───────────────────┘ └───────────────────┘ └───────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Message Flow

```
┌──────────┐                                      ┌──────────┐
│  Client  │                                      │  Server  │
└────┬─────┘                                      └────┬─────┘
     │                                                 │
     │  ──────── WebSocket Connect ────────────────>  │
     │  <─────── connection_ack {session_id} ───────  │
     │                                                 │
     │  ──────── audio_chunk (base64) ─────────────>  │
     │  ──────── audio_chunk (base64) ─────────────>  │
     │  <─────── transcript_partial {text} ─────────  │
     │  ──────── audio_chunk (base64) ─────────────>  │
     │  <─────── transcript_partial {text} ─────────  │
     │  ──────── audio_end ────────────────────────>  │
     │                                                 │
     │  <─────── transcript_final {text} ───────────  │
     │  <─────── status_update {generating} ────────  │
     │                                                 │
     │  <─────── response_chunk {text} ─────────────  │
     │  <─────── response_chunk {text} ─────────────  │
     │  <─────── response_chunk {text} ─────────────  │
     │                                                 │
     │  <─────── status_update {synthesizing} ──────  │
     │  <─────── response_complete {full_text} ─────  │
     │  <─────── status_update {idle} ──────────────  │
     │                                                 │
     └─────────────────────────────────────────────────┘
```

## Validation Rules

### Audio Chunks
- Maximum chunk size: 64KB (base64 encoded)
- Chunk interval: 100-200ms recommended
- Sample rate: 16000 Hz required for STT
- Maximum total duration: 60 seconds

### Text Input
- Maximum length: 10,000 characters
- Minimum length: 1 character

### Reconnection
- Maximum attempts: 5
- Backoff delays: 1s, 2s, 4s, 8s, 16s (exponential)
- Total timeout: ~31 seconds before giving up
