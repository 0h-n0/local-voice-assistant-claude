/**
 * Frontend API Contract: Voice Chat Web UI
 *
 * This file defines the TypeScript types and API client interface
 * for the frontend to communicate with the backend.
 *
 * Feature: 007-voice-chat-ui
 * Date: 2025-12-27
 */

// =============================================================================
// API Base Configuration
// =============================================================================

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// =============================================================================
// Conversation API Types
// =============================================================================

export type MessageRole = "user" | "assistant";

export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface ConversationSummary {
  id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail {
  id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

export type ConversationErrorCode =
  | "CONVERSATION_NOT_FOUND"
  | "MESSAGE_TOO_LONG"
  | "DATABASE_ERROR";

export interface ConversationErrorResponse {
  error_code: ConversationErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// Orchestrator API Types
// =============================================================================

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

export interface OrchestratorErrorResponse {
  error_code: OrchestratorErrorCode;
  message: string;
  details?: Record<string, unknown>;
  retry_after?: number;
}

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

export interface VoiceDialogueResponse {
  audio: Blob;
  metadata: ProcessingMetadata;
}

// =============================================================================
// TTS API Types
// =============================================================================

export type TTSErrorCode =
  | "EMPTY_TEXT"
  | "TEXT_TOO_LONG"
  | "MODEL_NOT_LOADED"
  | "SERVICE_BUSY"
  | "SYNTHESIS_FAILED";

export interface TTSErrorResponse {
  error_code: TTSErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// API Client Interface
// =============================================================================

export interface ApiClient {
  // Conversation endpoints
  getConversations(
    limit?: number,
    offset?: number
  ): Promise<ConversationListResponse>;
  getConversation(id: string): Promise<ConversationDetail>;
  deleteConversation(id: string): Promise<void>;

  // Voice dialogue endpoint
  sendVoiceMessage(
    audioBlob: Blob,
    speed?: number
  ): Promise<VoiceDialogueResponse>;

  // TTS endpoint (for replay)
  synthesizeSpeech(text: string, speed?: number): Promise<Blob>;
}

// =============================================================================
// API Client Implementation
// =============================================================================

/**
 * Parse processing metadata from response headers.
 */
function parseMetadataHeaders(headers: Headers): ProcessingMetadata {
  return {
    totalTime: parseFloat(headers.get("X-Processing-Time-Total") || "0"),
    sttTime: parseFloat(headers.get("X-Processing-Time-STT") || "0"),
    llmTime: parseFloat(headers.get("X-Processing-Time-LLM") || "0"),
    ttsTime: parseFloat(headers.get("X-Processing-Time-TTS") || "0"),
    inputDuration: parseFloat(headers.get("X-Input-Duration") || "0"),
    inputTextLength: parseInt(headers.get("X-Input-Text-Length") || "0", 10),
    outputTextLength: parseInt(headers.get("X-Output-Text-Length") || "0", 10),
    outputDuration: parseFloat(headers.get("X-Output-Duration") || "0"),
    sampleRate: parseInt(headers.get("X-Sample-Rate") || "44100", 10),
  };
}

/**
 * Create API client instance.
 */
export function createApiClient(baseUrl: string = API_BASE_URL): ApiClient {
  return {
    async getConversations(
      limit = 20,
      offset = 0
    ): Promise<ConversationListResponse> {
      const response = await fetch(
        `${baseUrl}/api/conversations?limit=${limit}&offset=${offset}`
      );

      if (!response.ok) {
        const error = (await response.json()) as ConversationErrorResponse;
        throw new Error(error.message);
      }

      return response.json();
    },

    async getConversation(id: string): Promise<ConversationDetail> {
      const response = await fetch(`${baseUrl}/api/conversations/${id}`);

      if (!response.ok) {
        const error = (await response.json()) as ConversationErrorResponse;
        throw new Error(error.message);
      }

      return response.json();
    },

    async deleteConversation(id: string): Promise<void> {
      const response = await fetch(`${baseUrl}/api/conversations/${id}`, {
        method: "DELETE",
      });

      if (!response.ok && response.status !== 204) {
        const error = (await response.json()) as ConversationErrorResponse;
        throw new Error(error.message);
      }
    },

    async sendVoiceMessage(
      audioBlob: Blob,
      speed = 1.0
    ): Promise<VoiceDialogueResponse> {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("speed", speed.toString());

      const response = await fetch(`${baseUrl}/api/orchestrator/dialogue`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = (await response.json()) as OrchestratorErrorResponse;
        throw new Error(error.message);
      }

      const audio = await response.blob();
      const metadata = parseMetadataHeaders(response.headers);

      return { audio, metadata };
    },

    async synthesizeSpeech(text: string, speed = 1.0): Promise<Blob> {
      const response = await fetch(`${baseUrl}/api/tts/synthesize`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text, speed }),
      });

      if (!response.ok) {
        const error = (await response.json()) as TTSErrorResponse;
        throw new Error(error.message);
      }

      return response.blob();
    },
  };
}

// =============================================================================
// Default API Client Instance
// =============================================================================

export const apiClient = createApiClient();
