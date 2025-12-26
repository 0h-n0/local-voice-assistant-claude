/**
 * WebSocket Message Types for Frontend.
 *
 * TypeScript types defining the WebSocket message protocol for real-time
 * communication between frontend and backend.
 */

// ============================================================================
// Enums
// ============================================================================

/**
 * Processing pipeline stages.
 * Displayed to user as status indicator.
 */
export type ProcessingStatus =
  | "idle"
  | "recording"
  | "transcribing"
  | "generating"
  | "synthesizing"
  | "playing"
  | "error";

/**
 * WebSocket connection status.
 * Displayed as connection indicator.
 */
export type ConnectionStatus =
  | "connecting"
  | "connected"
  | "reconnecting"
  | "disconnected"
  | "error";

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

/**
 * Supported audio formats for streaming.
 */
export type AudioFormat = "pcm16" | "opus" | "webm";

// ============================================================================
// Server -> Client Messages
// ============================================================================

/**
 * Partial transcript during speech recognition.
 * Sent continuously while user is speaking.
 */
export interface TranscriptPartialMessage {
  type: "transcript_partial";
  content: string;
  confidence?: number; // 0.0-1.0
  timestamp: string; // ISO 8601
}

/**
 * Final transcript after speech recognition completes.
 * Replaces all partial transcripts.
 */
export interface TranscriptFinalMessage {
  type: "transcript_final";
  content: string;
  confidence: number; // 0.0-1.0
  duration_ms: number; // Audio duration in milliseconds
  timestamp: string; // ISO 8601
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
 * Includes full text for verification.
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
  timestamp: string; // ISO 8601
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

// ============================================================================
// Client -> Server Messages
// ============================================================================

/**
 * Audio chunk during voice recording.
 * Sent continuously while recording is active.
 */
export interface AudioChunkMessage {
  type: "audio_chunk";
  data: string; // Base64 encoded audio data
  chunk_index: number; // Sequential chunk number
  sample_rate: number; // e.g., 16000
  format: AudioFormat; // Audio encoding format
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
 * All possible client-to-server message types.
 */
export type ClientMessage =
  | AudioChunkMessage
  | AudioEndMessage
  | TextInputMessage
  | CancelMessage
  | PongMessage;

// ============================================================================
// State Types
// ============================================================================

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

// ============================================================================
// Reducer Actions
// ============================================================================

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

/**
 * Transcript state actions.
 */
export type TranscriptAction =
  | { type: "PARTIAL_UPDATE"; payload: string }
  | { type: "FINAL_UPDATE"; payload: { text: string; confidence: number } }
  | { type: "CLEAR" };

/**
 * Processing status actions.
 */
export type ProcessingStatusAction =
  | { type: "SET_STATUS"; payload: ProcessingStatus }
  | { type: "APPEND_RESPONSE"; payload: string }
  | { type: "COMPLETE"; payload: string }
  | { type: "ERROR"; payload: { code: WebSocketErrorCode; message: string } }
  | { type: "RESET" };

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard for server messages.
 */
export function isServerMessage(data: unknown): data is ServerMessage {
  if (typeof data !== "object" || data === null) {
    return false;
  }
  const validTypes = [
    "transcript_partial",
    "transcript_final",
    "status_update",
    "response_chunk",
    "response_complete",
    "error",
    "connection_ack",
    "ping",
  ];
  return validTypes.includes((data as { type?: string }).type ?? "");
}

/**
 * Parse and validate server message.
 */
export function parseServerMessage(data: string): ServerMessage {
  const parsed = JSON.parse(data) as unknown;
  if (!isServerMessage(parsed)) {
    throw new Error(`Invalid server message: ${data}`);
  }
  return parsed;
}

// ============================================================================
// Constants
// ============================================================================

/**
 * Reconnection delays in milliseconds (exponential backoff).
 */
export const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 16000];

/**
 * Maximum reconnection attempts before giving up.
 */
export const MAX_RECONNECT_ATTEMPTS = RECONNECT_DELAYS.length;

/**
 * Heartbeat interval in milliseconds.
 */
export const HEARTBEAT_INTERVAL = 30000;

/**
 * Default audio chunk interval in milliseconds.
 */
export const AUDIO_CHUNK_INTERVAL = 100;

/**
 * Maximum audio duration in milliseconds.
 */
export const MAX_AUDIO_DURATION = 60000;
