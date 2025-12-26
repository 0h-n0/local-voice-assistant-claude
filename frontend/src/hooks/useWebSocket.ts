"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import type {
  ConnectionStatus,
  WebSocketState,
  ServerMessage,
  ClientMessage,
} from "@/types/websocket";
import {
  RECONNECT_DELAYS,
  MAX_RECONNECT_ATTEMPTS,
  parseServerMessage,
} from "@/types/websocket";
import { getWebSocketUrl, isWebSocketAvailable } from "@/lib/websocket";

/**
 * Return type for useWebSocket hook.
 */
export interface UseWebSocketReturn {
  /** Current connection state */
  state: WebSocketState;
  /** Connect to WebSocket server */
  connect: () => void;
  /** Disconnect from WebSocket server */
  disconnect: () => void;
  /** Send a message to the server */
  send: (message: ClientMessage) => boolean;
  /** Whether WebSocket is available in this environment */
  isAvailable: boolean;
}

/**
 * Options for useWebSocket hook.
 */
export interface UseWebSocketOptions {
  /** Auto-connect on mount (default: true) */
  autoConnect?: boolean;
  /** WebSocket URL (default: from getWebSocketUrl()) */
  url?: string;
  /** Callback when connection is established */
  onOpen?: () => void;
  /** Callback when a message is received */
  onMessage?: (message: ServerMessage) => void;
  /** Callback when connection is closed */
  onClose?: (event: CloseEvent) => void;
  /** Callback when an error occurs */
  onError?: (error: Event) => void;
  /** Callback when connection status changes */
  onStatusChange?: (status: ConnectionStatus) => void;
}

/**
 * Initial WebSocket state.
 */
const initialState: WebSocketState = {
  status: "disconnected",
  sessionId: null,
  reconnectAttempts: 0,
  error: null,
  lastMessageAt: null,
};

/**
 * Hook for managing WebSocket connection with auto-reconnection.
 */
export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketReturn {
  const {
    autoConnect = true,
    url,
    onOpen,
    onMessage,
    onClose,
    onError,
    onStatusChange,
  } = options;

  const [state, setState] = useState<WebSocketState>(initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );
  const reconnectAttemptRef = useRef(0);
  const connectRef = useRef<() => void>(() => {});
  const isAvailable = isWebSocketAvailable();

  /**
   * Update state helper.
   */
  const updateState = useCallback(
    (updates: Partial<WebSocketState>) => {
      setState((prev) => {
        const newState = { ...prev, ...updates };
        if (updates.status && updates.status !== prev.status) {
          onStatusChange?.(updates.status);
        }
        return newState;
      });
    },
    [onStatusChange]
  );

  /**
   * Get reconnection delay for current attempt.
   */
  const getReconnectDelay = useCallback((attempt: number): number => {
    const index = Math.min(attempt, RECONNECT_DELAYS.length - 1);
    return RECONNECT_DELAYS[index];
  }, []);

  /**
   * Schedule a reconnection attempt.
   */
  const scheduleReconnect = useCallback(() => {
    if (reconnectAttemptRef.current >= MAX_RECONNECT_ATTEMPTS) {
      updateState({
        status: "error",
        error: "Maximum reconnection attempts reached",
      });
      return;
    }

    const delay = getReconnectDelay(reconnectAttemptRef.current);
    reconnectAttemptRef.current += 1;

    updateState({
      status: "reconnecting",
      reconnectAttempts: reconnectAttemptRef.current,
    });

    reconnectTimeoutRef.current = setTimeout(() => {
      connectRef.current();
    }, delay);
  }, [getReconnectDelay, updateState]);

  /**
   * Handle incoming WebSocket message.
   */
  const handleMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const message = parseServerMessage(event.data as string);

        // Update last message timestamp
        updateState({ lastMessageAt: new Date() });

        // Handle connection_ack to get session ID
        if (message.type === "connection_ack") {
          updateState({ sessionId: message.session_id });
        }

        // Handle ping with pong response
        if (message.type === "ping" && wsRef.current?.readyState === WebSocket.OPEN) {
          wsRef.current.send(
            JSON.stringify({
              type: "pong",
              timestamp: message.timestamp,
            })
          );
        }

        // Call user callback
        onMessage?.(message);
      } catch (error) {
        console.error("[useWebSocket] Parse error:", error);
      }
    },
    [onMessage, updateState]
  );

  /**
   * Connect to WebSocket server.
   */
  const connect = useCallback(() => {
    if (!isAvailable) {
      updateState({
        status: "error",
        error: "WebSocket is not available in this environment",
      });
      return;
    }

    // Close existing connection if any
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    updateState({ status: "connecting", error: null });

    const wsUrl = url || getWebSocketUrl();

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttemptRef.current = 0;
        updateState({
          status: "connected",
          reconnectAttempts: 0,
          error: null,
        });
        onOpen?.();
      };

      ws.onmessage = handleMessage;

      ws.onclose = (event) => {
        wsRef.current = null;
        onClose?.(event);

        // Only reconnect if not a clean close
        if (event.code !== 1000) {
          scheduleReconnect();
        } else {
          updateState({
            status: "disconnected",
            sessionId: null,
          });
        }
      };

      ws.onerror = (error) => {
        console.error("[useWebSocket] Error:", error);
        onError?.(error);
      };
    } catch (error) {
      console.error("[useWebSocket] Connection error:", error);
      updateState({
        status: "error",
        error: error instanceof Error ? error.message : "Connection failed",
      });
      scheduleReconnect();
    }
  }, [
    isAvailable,
    url,
    handleMessage,
    onOpen,
    onClose,
    onError,
    scheduleReconnect,
    updateState,
  ]);

  // Keep connectRef in sync with connect function
  connectRef.current = connect;

  /**
   * Disconnect from WebSocket server.
   */
  const disconnect = useCallback(() => {
    // Clear any pending reconnect
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    reconnectAttemptRef.current = 0;

    if (wsRef.current) {
      wsRef.current.close(1000, "Client disconnect");
      wsRef.current = null;
    }

    updateState({
      status: "disconnected",
      sessionId: null,
      reconnectAttempts: 0,
      error: null,
    });
  }, [updateState]);

  /**
   * Send a message to the server.
   */
  const send = useCallback((message: ClientMessage): boolean => {
    if (wsRef.current?.readyState !== WebSocket.OPEN) {
      console.warn("[useWebSocket] Cannot send: not connected");
      return false;
    }

    try {
      wsRef.current.send(JSON.stringify(message));
      return true;
    } catch (error) {
      console.error("[useWebSocket] Send error:", error);
      return false;
    }
  }, []);

  /**
   * Auto-connect on mount if enabled.
   */
  useEffect(() => {
    if (autoConnect && isAvailable) {
      connect();
    }

    return () => {
      // Cleanup on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, "Component unmount");
      }
    };
    // Only run on mount/unmount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    state,
    connect,
    disconnect,
    send,
    isAvailable,
  };
}
