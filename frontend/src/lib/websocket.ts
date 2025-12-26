/**
 * WebSocket Client Utility.
 *
 * Connection helpers and message serialization for real-time communication
 * with the backend WebSocket endpoint.
 */

import type {
  ClientMessage,
  ServerMessage,
  ConnectionStatus,
} from "@/types/websocket";
import {
  RECONNECT_DELAYS,
  MAX_RECONNECT_ATTEMPTS,
  HEARTBEAT_INTERVAL,
  parseServerMessage,
} from "@/types/websocket";

// Re-export constants for convenience
export { RECONNECT_DELAYS, MAX_RECONNECT_ATTEMPTS, HEARTBEAT_INTERVAL };

/**
 * Default WebSocket URL (same host as API, /ws/realtime path).
 */
export function getWebSocketUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const wsProtocol = apiUrl.startsWith("https://") ? "wss://" : "ws://";
  const host = apiUrl.replace(/^https?:\/\//, "");
  return `${wsProtocol}${host}/ws/realtime`;
}

/**
 * Check if WebSocket is available in the current environment.
 */
export function isWebSocketAvailable(): boolean {
  return typeof WebSocket !== "undefined";
}

/**
 * Serialize a client message to JSON string.
 */
export function serializeMessage(message: ClientMessage): string {
  return JSON.stringify(message);
}

/**
 * Create an audio chunk message.
 */
export function createAudioChunkMessage(
  data: string,
  chunkIndex: number,
  sampleRate = 16000,
  format: "pcm16" | "opus" | "webm" = "webm"
): ClientMessage {
  return {
    type: "audio_chunk",
    data,
    chunk_index: chunkIndex,
    sample_rate: sampleRate,
    format,
  };
}

/**
 * Create an audio end message.
 */
export function createAudioEndMessage(
  totalChunks: number,
  totalDurationMs: number
): ClientMessage {
  return {
    type: "audio_end",
    total_chunks: totalChunks,
    total_duration_ms: totalDurationMs,
  };
}

/**
 * Create a text input message.
 */
export function createTextInputMessage(
  content: string,
  conversationId?: string
): ClientMessage {
  return {
    type: "text_input",
    content,
    conversation_id: conversationId,
  };
}

/**
 * Create a cancel message.
 */
export function createCancelMessage(reason?: string): ClientMessage {
  return {
    type: "cancel",
    reason,
  };
}

/**
 * Create a pong message (response to server ping).
 */
export function createPongMessage(serverTimestamp: string): ClientMessage {
  return {
    type: "pong",
    timestamp: serverTimestamp,
  };
}

/**
 * Get reconnection delay for the given attempt number.
 * Uses exponential backoff defined in RECONNECT_DELAYS.
 */
export function getReconnectDelay(attempt: number): number {
  const index = Math.min(attempt, RECONNECT_DELAYS.length - 1);
  return RECONNECT_DELAYS[index];
}

/**
 * Check if more reconnection attempts are allowed.
 */
export function canReconnect(attempt: number): boolean {
  return attempt < MAX_RECONNECT_ATTEMPTS;
}

/**
 * WebSocket connection options.
 */
export interface WebSocketOptions {
  /** URL to connect to (default: getWebSocketUrl()) */
  url?: string;
  /** Called when connection is established */
  onOpen?: () => void;
  /** Called when a message is received */
  onMessage?: (message: ServerMessage) => void;
  /** Called when connection is closed */
  onClose?: (event: CloseEvent) => void;
  /** Called when an error occurs */
  onError?: (error: Event) => void;
  /** Called when connection status changes */
  onStatusChange?: (status: ConnectionStatus) => void;
}

/**
 * WebSocket connection manager.
 * Handles connection lifecycle, reconnection, and message handling.
 */
export class WebSocketConnection {
  private ws: WebSocket | null = null;
  private options: WebSocketOptions;
  private reconnectAttempt = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
  private status: ConnectionStatus = "disconnected";

  constructor(options: WebSocketOptions = {}) {
    this.options = options;
  }

  /**
   * Get current connection status.
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Connect to the WebSocket server.
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.setStatus("connecting");
    const url = this.options.url || getWebSocketUrl();

    try {
      this.ws = new WebSocket(url);
      this.setupEventHandlers();
    } catch {
      this.setStatus("error");
      this.scheduleReconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server.
   */
  disconnect(): void {
    this.clearTimers();
    this.reconnectAttempt = 0;

    if (this.ws) {
      this.ws.close(1000, "Client disconnect");
      this.ws = null;
    }

    this.setStatus("disconnected");
  }

  /**
   * Send a message to the server.
   */
  send(message: ClientMessage): boolean {
    if (this.ws?.readyState !== WebSocket.OPEN) {
      console.warn("[WebSocket] Cannot send: not connected");
      return false;
    }

    try {
      this.ws.send(serializeMessage(message));
      return true;
    } catch (error) {
      console.error("[WebSocket] Send error:", error);
      return false;
    }
  }

  /**
   * Check if connection is open.
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private setStatus(status: ConnectionStatus): void {
    if (this.status !== status) {
      this.status = status;
      this.options.onStatusChange?.(status);
    }
  }

  private setupEventHandlers(): void {
    if (!this.ws) return;

    this.ws.onopen = () => {
      this.reconnectAttempt = 0;
      this.setStatus("connected");
      this.startHeartbeat();
      this.options.onOpen?.();
    };

    this.ws.onmessage = (event) => {
      try {
        const message = parseServerMessage(event.data as string);
        this.options.onMessage?.(message);
      } catch (error) {
        console.error("[WebSocket] Parse error:", error);
      }
    };

    this.ws.onclose = (event) => {
      this.stopHeartbeat();
      this.options.onClose?.(event);

      // Only attempt reconnect if not a clean close
      if (event.code !== 1000) {
        this.scheduleReconnect();
      } else {
        this.setStatus("disconnected");
      }
    };

    this.ws.onerror = (error) => {
      console.error("[WebSocket] Error:", error);
      this.options.onError?.(error);
    };
  }

  private scheduleReconnect(): void {
    if (!canReconnect(this.reconnectAttempt)) {
      this.setStatus("error");
      return;
    }

    this.setStatus("reconnecting");
    const delay = getReconnectDelay(this.reconnectAttempt);
    this.reconnectAttempt++;

    this.reconnectTimeout = setTimeout(() => {
      this.connect();
    }, delay);
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    // Heartbeat is handled by ping/pong messages from server
    // Client responds to server pings in the onMessage handler
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  private clearTimers(): void {
    this.stopHeartbeat();
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }
}

/**
 * Create a new WebSocket connection instance.
 */
export function createWebSocketConnection(
  options?: WebSocketOptions
): WebSocketConnection {
  return new WebSocketConnection(options);
}
