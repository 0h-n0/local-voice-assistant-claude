/**
 * TypeScript types for audio state and related functionality.
 */

// =============================================================================
// Playback State
// =============================================================================

/**
 * Audio playback state.
 */
export type PlaybackState = "idle" | "playing" | "paused" | "loading";

// =============================================================================
// Audio State Types
// =============================================================================

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

/**
 * Initial audio state.
 */
export const initialAudioState: AudioState = {
  isRecording: false,
  playbackState: "idle",
  isMuted: false,
  currentPlayingMessageId: null,
  recordingError: null,
  playbackError: null,
};

// =============================================================================
// Voice Recorder Types
// =============================================================================

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

// =============================================================================
// Audio Player Types
// =============================================================================

/**
 * Audio player hook return type.
 */
export interface UseAudioPlayerReturn {
  /** Current playback state */
  state: PlaybackState;

  /** Play audio from blob */
  play: (audio: Blob) => Promise<void>;

  /** Play audio from text (re-request TTS) */
  playFromText: (text: string, speed?: number) => Promise<void>;

  /** Stop current playback */
  stop: () => void;

  /** Error message if playback failed */
  error: string | null;
}

// =============================================================================
// Orchestrator Types
// =============================================================================

/**
 * Orchestrator error codes.
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
 */
export interface OrchestratorErrorResponse {
  error_code: OrchestratorErrorCode;
  message: string;
  details?: Record<string, unknown>;
  retry_after?: number;
}

/**
 * Processing metadata from response headers.
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
 */
export interface VoiceDialogueResponse {
  audio: Blob;
  metadata: ProcessingMetadata;
}

// =============================================================================
// TTS Types
// =============================================================================

/**
 * TTS error codes.
 */
export type TTSErrorCode =
  | "EMPTY_TEXT"
  | "TEXT_TOO_LONG"
  | "MODEL_NOT_LOADED"
  | "SERVICE_BUSY"
  | "SYNTHESIS_FAILED";

/**
 * TTS error response.
 */
export interface TTSErrorResponse {
  error_code: TTSErrorCode;
  message: string;
  details?: Record<string, unknown>;
}
