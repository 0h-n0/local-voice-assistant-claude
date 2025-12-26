/**
 * API client utility for communicating with the backend.
 */

import type { HealthResponse } from "@/types";
import type {
  ConversationListResponse,
  ConversationDetail,
  ConversationErrorResponse,
} from "@/types/conversation";
import type {
  VoiceDialogueResponse,
  ProcessingMetadata,
  OrchestratorErrorResponse,
  TTSErrorResponse,
} from "@/types/audio";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// =============================================================================
// Health Endpoint
// =============================================================================

/**
 * Fetches the health status from the backend API.
 * @returns Promise resolving to the health response.
 * @throws Error if the request fails.
 */
export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }

  return response.json() as Promise<HealthResponse>;
}

// =============================================================================
// Conversation Endpoints
// =============================================================================

/**
 * Fetches list of conversations with pagination.
 */
export async function getConversations(
  limit = 20,
  offset = 0
): Promise<ConversationListResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/conversations?limit=${limit}&offset=${offset}`
  );

  if (!response.ok) {
    const error = (await response.json()) as ConversationErrorResponse;
    throw new Error(error.message);
  }

  return response.json() as Promise<ConversationListResponse>;
}

/**
 * Fetches a single conversation by ID.
 */
export async function getConversation(id: string): Promise<ConversationDetail> {
  const response = await fetch(`${API_BASE_URL}/api/conversations/${id}`);

  if (!response.ok) {
    const error = (await response.json()) as ConversationErrorResponse;
    throw new Error(error.message);
  }

  return response.json() as Promise<ConversationDetail>;
}

/**
 * Deletes a conversation by ID.
 */
export async function deleteConversation(id: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/conversations/${id}`, {
    method: "DELETE",
  });

  if (!response.ok && response.status !== 204) {
    const error = (await response.json()) as ConversationErrorResponse;
    throw new Error(error.message);
  }
}

// =============================================================================
// Orchestrator Endpoint
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
 * Sends a voice message to the orchestrator and receives audio response.
 * @param audioBlob - The recorded audio blob
 * @param conversationId - Optional conversation ID to continue
 * @param speed - TTS speech speed (default: 1.0)
 */
export async function sendVoiceMessage(
  audioBlob: Blob,
  conversationId?: string,
  speed = 1.0
): Promise<VoiceDialogueResponse> {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");
  formData.append("speed", speed.toString());
  if (conversationId) {
    formData.append("conversation_id", conversationId);
  }

  const response = await fetch(`${API_BASE_URL}/api/orchestrator/dialogue`, {
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
}

// =============================================================================
// TTS Endpoint
// =============================================================================

/**
 * Synthesizes speech from text.
 * Used for replaying assistant responses.
 * @param text - The text to synthesize
 * @param speed - Speech speed (default: 1.0)
 */
export async function synthesizeSpeech(
  text: string,
  speed = 1.0
): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/tts/synthesize`, {
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
}

// =============================================================================
// API Client Interface (for dependency injection)
// =============================================================================

export interface ApiClient {
  getHealth(): Promise<HealthResponse>;
  getConversations(limit?: number, offset?: number): Promise<ConversationListResponse>;
  getConversation(id: string): Promise<ConversationDetail>;
  deleteConversation(id: string): Promise<void>;
  sendVoiceMessage(
    audioBlob: Blob,
    conversationId?: string,
    speed?: number
  ): Promise<VoiceDialogueResponse>;
  synthesizeSpeech(text: string, speed?: number): Promise<Blob>;
}

/**
 * Default API client using module functions.
 */
export const apiClient: ApiClient = {
  getHealth,
  getConversations,
  getConversation,
  deleteConversation,
  sendVoiceMessage,
  synthesizeSpeech,
};
