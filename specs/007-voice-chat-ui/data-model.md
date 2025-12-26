# Data Model: Voice Chat Web UI

**Feature**: 007-voice-chat-ui
**Date**: 2025-12-27

## Overview

This document defines the frontend TypeScript types that mirror backend Pydantic models and add UI-specific state management types.

## Backend API Types (Mirror of Pydantic Models)

### Conversation Types

```typescript
/**
 * Message sender role.
 * Matches backend MessageRole enum.
 */
export type MessageRole = "user" | "assistant";

/**
 * Message in API response.
 * Matches backend MessageResponse model.
 */
export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  created_at: string; // ISO 8601 timestamp
}

/**
 * Conversation summary for list view.
 * Matches backend ConversationSummary model.
 */
export interface ConversationSummary {
  id: string; // UUID
  message_count: number;
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * Full conversation with messages.
 * Matches backend ConversationDetail model.
 */
export interface ConversationDetail {
  id: string; // UUID
  messages: Message[];
  created_at: string; // ISO 8601 timestamp
  updated_at: string; // ISO 8601 timestamp
}

/**
 * Paginated conversation list response.
 * Matches backend ConversationListResponse model.
 */
export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

/**
 * Conversation error codes.
 * Matches backend ConversationErrorCode enum.
 */
export type ConversationErrorCode =
  | "CONVERSATION_NOT_FOUND"
  | "MESSAGE_TOO_LONG"
  | "DATABASE_ERROR";

/**
 * Conversation error response.
 * Matches backend ConversationErrorResponse model.
 */
export interface ConversationErrorResponse {
  error_code: ConversationErrorCode;
  message: string;
  details?: Record<string, unknown>;
}
```

### Orchestrator Types

```typescript
/**
 * Orchestrator error codes.
 * Matches backend OrchestratorErrorCode enum.
 */
export type OrchestratorErrorCode =
  | "INVALID_AUDIO_FORMAT"
  | "AUDIO_TOO_SHORT"
  | "AUDIO_TOO_LONG"
  | "SPEECH_RECOGNITION_FAILED"
  | "STT_SERVICE_UNAVAILABLE"
  | "LLM_SERVICE_UNAVAILABLE"
  | "LLM_RATE_LIMITED"
  | "LLM_CONNECTION_ERROR"
  | "TTS_SERVICE_UNAVAILABLE"
  | "SYNTHESIS_FAILED"
  | "PROCESSING_TIMEOUT"
  | "TOO_MANY_REQUESTS";

/**
 * Orchestrator error response.
 * Matches backend OrchestratorErrorResponse model.
 */
export interface OrchestratorErrorResponse {
  error_code: OrchestratorErrorCode;
  message: string;
  details?: Record<string, unknown>;
  retry_after?: number;
}

/**
 * Processing metadata from response headers.
 * Parsed from X-* headers in dialogue response.
 */
export interface ProcessingMetadata {
  totalTime: number;
  sttTime: number;
  llmTime: number;
  ttsTime: number;
  inputDuration: number;
  inputTextLength: number;
  outputTextLength: number;
  outputDuration: number;
  sampleRate: number;
}

/**
 * Voice dialogue response.
 * Combined audio blob and metadata.
 */
export interface VoiceDialogueResponse {
  audio: Blob;
  metadata: ProcessingMetadata;
}
```

### TTS Types

```typescript
/**
 * TTS error codes.
 * Matches backend TTSErrorCode enum.
 */
export type TTSErrorCode =
  | "EMPTY_TEXT"
  | "TEXT_TOO_LONG"
  | "MODEL_NOT_LOADED"
  | "SERVICE_BUSY"
  | "SYNTHESIS_FAILED";

/**
 * TTS error response.
 * Matches backend TTSErrorResponse model.
 */
export interface TTSErrorResponse {
  error_code: TTSErrorCode;
  message: string;
  details?: Record<string, unknown>;
}
```

## Frontend UI State Types

### Chat State

```typescript
/**
 * Global chat state managed by ChatContext.
 */
export interface ChatState {
  /** List of conversation summaries for sidebar */
  conversations: ConversationSummary[];

  /** Currently selected conversation ID */
  currentConversationId: string | null;

  /** Messages in current conversation */
  messages: Message[];

  /** Whether data is being loaded */
  isLoading: boolean;

  /** Whether a message is being sent/processed */
  isSending: boolean;

  /** Error message to display */
  error: string | null;
}

/**
 * Chat state actions.
 */
export type ChatAction =
  | { type: "SET_CONVERSATIONS"; payload: ConversationSummary[] }
  | { type: "ADD_CONVERSATION"; payload: ConversationSummary }
  | { type: "REMOVE_CONVERSATION"; payload: string }
  | { type: "SELECT_CONVERSATION"; payload: string | null }
  | { type: "SET_MESSAGES"; payload: Message[] }
  | { type: "ADD_MESSAGE"; payload: Message }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_SENDING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "CLEAR_ERROR" };
```

### Audio State

```typescript
/**
 * Audio playback state.
 */
export type PlaybackState = "idle" | "playing" | "paused" | "loading";

/**
 * Audio state managed by AudioContext.
 */
export interface AudioState {
  /** Whether currently recording voice input */
  isRecording: boolean;

  /** Current playback state */
  playbackState: PlaybackState;

  /** Whether auto-play is muted */
  isMuted: boolean;

  /** ID of message currently playing (for replay button state) */
  currentPlayingMessageId: number | null;

  /** Recording error message */
  recordingError: string | null;

  /** Playback error message */
  playbackError: string | null;
}

/**
 * Audio state actions.
 */
export type AudioAction =
  | { type: "START_RECORDING" }
  | { type: "STOP_RECORDING" }
  | { type: "SET_RECORDING_ERROR"; payload: string | null }
  | { type: "START_PLAYBACK"; payload: number }
  | { type: "STOP_PLAYBACK" }
  | { type: "SET_PLAYBACK_STATE"; payload: PlaybackState }
  | { type: "SET_PLAYBACK_ERROR"; payload: string | null }
  | { type: "TOGGLE_MUTE" }
  | { type: "SET_MUTED"; payload: boolean };
```

### Voice Recorder Hook

```typescript
/**
 * Voice recorder hook state.
 */
export interface VoiceRecorderState {
  /** Whether recording is active */
  isRecording: boolean;

  /** Recording duration in seconds */
  duration: number;

  /** Error message if permission denied or recording failed */
  error: string | null;

  /** Whether microphone permission is granted */
  hasPermission: boolean | null;
}

/**
 * Voice recorder hook return type.
 */
export interface UseVoiceRecorderReturn {
  /** Current recording state */
  state: VoiceRecorderState;

  /** Start recording */
  startRecording: () => Promise<void>;

  /** Stop recording and return audio blob */
  stopRecording: () => Promise<Blob | null>;

  /** Cancel recording without returning blob */
  cancelRecording: () => void;

  /** Request microphone permission */
  requestPermission: () => Promise<boolean>;
}
```

### Audio Player Hook

```typescript
/**
 * Audio player hook return type.
 */
export interface UseAudioPlayerReturn {
  /** Current playback state */
  state: PlaybackState;

  /** Play audio from blob */
  play: (audio: Blob) => Promise<void>;

  /** Stop current playback */
  stop: () => void;

  /** Error message if playback failed */
  error: string | null;
}
```

## Entity Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend State                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │   ChatContext   │         │  AudioContext   │               │
│  │                 │         │                 │               │
│  │ - conversations │         │ - isRecording   │               │
│  │ - messages      │         │ - playbackState │               │
│  │ - currentId     │         │ - isMuted       │               │
│  └────────┬────────┘         └────────┬────────┘               │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │ ConversationList│         │  VoiceButton    │               │
│  │ (Sidebar)       │         │  (Recording)    │               │
│  └─────────────────┘         └─────────────────┘               │
│           │                           │                         │
│           ▼                           ▼                         │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  MessageList    │         │  AudioPlayer    │               │
│  │  (Chat Area)    │◄────────│  (Playback)     │               │
│  └─────────────────┘         └─────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend APIs                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GET  /api/conversations          → ConversationListResponse   │
│  GET  /api/conversations/{id}     → ConversationDetail         │
│  DELETE /api/conversations/{id}   → 204 No Content             │
│                                                                 │
│  POST /api/orchestrator/dialogue  → audio/wav + headers        │
│       (multipart: audio file)                                   │
│                                                                 │
│  POST /api/tts/synthesize         → audio/wav                  │
│       (JSON: { text, speed })     (for replay)                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Validation Rules

### Message Content
- Maximum length: 10,000 characters (enforced by backend)
- Minimum length: 1 character

### Conversation ID
- Format: UUID v4 (validated by backend)
- Generated by orchestrator service on first message

### Audio Input
- Minimum duration: 0.5 seconds (enforced by backend)
- Maximum duration: 300 seconds (5 minutes, enforced by backend)
- Supported formats: WAV, MP3, WebM (converted by pydub)

### TTS Text
- Maximum length: 5,000 characters
- Language: Japanese (primary)
