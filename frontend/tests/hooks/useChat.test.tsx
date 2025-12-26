/**
 * Tests for useChat hook.
 * @jest-environment jsdom
 */

import { renderHook, act } from "@testing-library/react";
import React from "react";
import { ChatProvider } from "@/components/providers/ChatContext";
import { AudioProvider } from "@/components/providers/AudioContext";

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Import after mocks
import { useChat } from "@/hooks/useChat";

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ChatProvider>
    <AudioProvider>{children}</AudioProvider>
  </ChatProvider>
);

describe("useChat", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("initial state", () => {
    it("should start with empty messages", () => {
      const { result } = renderHook(() => useChat(), { wrapper });
      expect(result.current.messages).toEqual([]);
    });

    it("should start with isSending false", () => {
      const { result } = renderHook(() => useChat(), { wrapper });
      expect(result.current.isSending).toBe(false);
    });

    it("should start with no error", () => {
      const { result } = renderHook(() => useChat(), { wrapper });
      expect(result.current.error).toBeNull();
    });
  });

  describe("addMessage", () => {
    it("should add a message to the list", () => {
      const { result } = renderHook(() => useChat(), { wrapper });

      act(() => {
        result.current.addMessage({
          id: 1,
          role: "user",
          content: "Hello",
          created_at: "2025-12-27T10:00:00Z",
        });
      });

      expect(result.current.messages).toHaveLength(1);
      expect(result.current.messages[0].content).toBe("Hello");
    });
  });

  describe("clearMessages", () => {
    it("should clear all messages", () => {
      const { result } = renderHook(() => useChat(), { wrapper });

      act(() => {
        result.current.addMessage({
          id: 1,
          role: "user",
          content: "Hello",
          created_at: "2025-12-27T10:00:00Z",
        });
      });

      expect(result.current.messages).toHaveLength(1);

      act(() => {
        result.current.clearMessages();
      });

      expect(result.current.messages).toHaveLength(0);
    });
  });

  describe("setError", () => {
    it("should set error message", () => {
      const { result } = renderHook(() => useChat(), { wrapper });

      act(() => {
        result.current.setError("Something went wrong");
      });

      expect(result.current.error).toBe("Something went wrong");
    });
  });

  describe("clearError", () => {
    it("should clear error message", () => {
      const { result } = renderHook(() => useChat(), { wrapper });

      act(() => {
        result.current.setError("Something went wrong");
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });
});
