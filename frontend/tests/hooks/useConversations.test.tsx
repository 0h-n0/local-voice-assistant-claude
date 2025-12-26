/**
 * Tests for useConversations hook.
 * @jest-environment jsdom
 */

import { renderHook, act } from "@testing-library/react";
import React from "react";
import { ChatProvider } from "@/components/providers/ChatContext";

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Import after mocks
import { useConversations } from "@/hooks/useConversations";

const mockConversations = [
  {
    id: "conv-1",
    message_count: 3,
    created_at: "2025-12-27T10:00:00Z",
    updated_at: "2025-12-27T11:00:00Z",
  },
  {
    id: "conv-2",
    message_count: 5,
    created_at: "2025-12-26T09:00:00Z",
    updated_at: "2025-12-26T10:00:00Z",
  },
];

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <ChatProvider>{children}</ChatProvider>
);

describe("useConversations", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("fetchConversations", () => {
    it("should fetch conversations from API", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            conversations: mockConversations,
            total: 2,
            limit: 20,
            offset: 0,
          }),
      });

      const { result } = renderHook(() => useConversations(), { wrapper });

      await act(async () => {
        await result.current.fetchConversations();
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/conversations")
      );
      expect(result.current.conversations).toHaveLength(2);
    });

    it("should set loading state during fetch", async () => {
      let resolvePromise: (value: unknown) => void;
      const promise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockFetch.mockReturnValue({
        ok: true,
        json: () => promise,
      });

      const { result } = renderHook(() => useConversations(), { wrapper });

      act(() => {
        result.current.fetchConversations();
      });

      expect(result.current.isLoading).toBe(true);

      await act(async () => {
        resolvePromise!({
          conversations: [],
          total: 0,
          limit: 20,
          offset: 0,
        });
      });

      expect(result.current.isLoading).toBe(false);
    });

    it("should handle fetch error", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      const { result } = renderHook(() => useConversations(), { wrapper });

      await act(async () => {
        await result.current.fetchConversations();
      });

      expect(result.current.error).toBeTruthy();
    });
  });

  describe("selectConversation", () => {
    it("should select a conversation and fetch its messages", async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve({
              conversations: mockConversations,
              total: 2,
              limit: 20,
              offset: 0,
            }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve({
              id: "conv-1",
              messages: [
                { id: 1, role: "user", content: "Hello", created_at: "2025-12-27T10:00:00Z" },
                { id: 2, role: "assistant", content: "Hi there!", created_at: "2025-12-27T10:00:01Z" },
              ],
              created_at: "2025-12-27T10:00:00Z",
              updated_at: "2025-12-27T11:00:00Z",
            }),
        });

      const { result } = renderHook(() => useConversations(), { wrapper });

      await act(async () => {
        await result.current.fetchConversations();
      });

      await act(async () => {
        await result.current.selectConversation("conv-1");
      });

      expect(result.current.currentConversationId).toBe("conv-1");
    });
  });

  describe("deleteConversation", () => {
    it("should delete a conversation", async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: () =>
            Promise.resolve({
              conversations: mockConversations,
              total: 2,
              limit: 20,
              offset: 0,
            }),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 204,
        });

      const { result } = renderHook(() => useConversations(), { wrapper });

      await act(async () => {
        await result.current.fetchConversations();
      });

      await act(async () => {
        await result.current.deleteConversation("conv-1");
      });

      expect(mockFetch).toHaveBeenLastCalledWith(
        expect.stringContaining("/api/conversations/conv-1"),
        expect.objectContaining({ method: "DELETE" })
      );
    });
  });
});
