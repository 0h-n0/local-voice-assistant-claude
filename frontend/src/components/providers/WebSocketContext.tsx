"use client";

import {
  createContext,
  useContext,
  useCallback,
  type ReactNode,
} from "react";
import {
  useWebSocket,
  type UseWebSocketReturn,
  type UseWebSocketOptions,
} from "@/hooks/useWebSocket";
import type { ServerMessage } from "@/types/websocket";

// =============================================================================
// Context Definition
// =============================================================================

type WebSocketContextValue = UseWebSocketReturn;

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

// =============================================================================
// Provider Component
// =============================================================================

interface WebSocketProviderProps {
  children: ReactNode;
  /** Custom WebSocket options */
  options?: Omit<UseWebSocketOptions, "onMessage">;
  /** Global message handler */
  onMessage?: (message: ServerMessage) => void;
}

export function WebSocketProvider({
  children,
  options = {},
  onMessage,
}: WebSocketProviderProps) {
  const handleMessage = useCallback(
    (message: ServerMessage) => {
      // Call global handler if provided
      onMessage?.(message);
    },
    [onMessage]
  );

  const ws = useWebSocket({
    ...options,
    onMessage: handleMessage,
  });

  return (
    <WebSocketContext.Provider value={ws}>
      {children}
    </WebSocketContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Use the WebSocket context.
 * Must be used within a WebSocketProvider.
 */
export function useWebSocketContext(): WebSocketContextValue {
  const context = useContext(WebSocketContext);

  if (!context) {
    throw new Error(
      "useWebSocketContext must be used within a WebSocketProvider"
    );
  }

  return context;
}

// =============================================================================
// Convenience Hooks
// =============================================================================

/**
 * Get WebSocket connection status.
 */
export function useConnectionStatus() {
  const { state } = useWebSocketContext();
  return state.status;
}

/**
 * Get WebSocket session ID.
 */
export function useSessionId() {
  const { state } = useWebSocketContext();
  return state.sessionId;
}

/**
 * Get whether WebSocket is connected.
 */
export function useIsConnected() {
  const { state } = useWebSocketContext();
  return state.status === "connected";
}

/**
 * Get a function to send messages.
 */
export function useSendMessage() {
  const { send } = useWebSocketContext();
  return send;
}
