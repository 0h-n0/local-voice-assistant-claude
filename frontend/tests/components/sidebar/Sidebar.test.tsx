/**
 * Tests for Sidebar component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { ChatProvider } from "@/components/providers/ChatContext";

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <ChatProvider>{children}</ChatProvider>
);

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

describe("Sidebar", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockResolvedValue({
      ok: true,
      json: () =>
        Promise.resolve({
          conversations: mockConversations,
          total: 2,
          limit: 20,
          offset: 0,
        }),
    });
  });

  describe("rendering", () => {
    it("should render sidebar with header", () => {
      render(
        <Wrapper>
          <Sidebar />
        </Wrapper>
      );

      // Should have a header or title
      expect(
        screen.getByRole("heading", { level: 2 }) ||
          screen.getByText(/会話/i) ||
          screen.getByText(/チャット/i)
      ).toBeInTheDocument();
    });

    it("should render New Chat button", () => {
      render(
        <Wrapper>
          <Sidebar />
        </Wrapper>
      );

      expect(
        screen.getByRole("button", { name: /新しいチャット|New Chat/i })
      ).toBeInTheDocument();
    });
  });

  describe("visibility", () => {
    it("should be visible when isOpen is true", () => {
      const { container } = render(
        <Wrapper>
          <Sidebar isOpen={true} />
        </Wrapper>
      );

      const sidebar = container.firstChild as HTMLElement;
      // Should not have hidden class
      expect(sidebar).not.toHaveClass("hidden");
    });

    it("should be hidden when isOpen is false", () => {
      const { container } = render(
        <Wrapper>
          <Sidebar isOpen={false} />
        </Wrapper>
      );

      const sidebar = container.firstChild as HTMLElement;
      // Should have hidden or translate class for mobile
      expect(
        sidebar.classList.contains("hidden") ||
          sidebar.classList.contains("-translate-x-full")
      ).toBeTruthy();
    });
  });

  describe("close button", () => {
    it("should call onClose when close button is clicked", () => {
      const onClose = jest.fn();

      render(
        <Wrapper>
          <Sidebar isOpen={true} onClose={onClose} />
        </Wrapper>
      );

      const closeButton = screen.getByLabelText(/閉じる|close/i);
      fireEvent.click(closeButton);

      expect(onClose).toHaveBeenCalled();
    });
  });

  describe("new conversation", () => {
    it("should call onNewConversation when New Chat button is clicked", () => {
      const onNewConversation = jest.fn();

      render(
        <Wrapper>
          <Sidebar onNewConversation={onNewConversation} />
        </Wrapper>
      );

      const newChatButton = screen.getByRole("button", {
        name: /新しいチャット|New Chat/i,
      });
      fireEvent.click(newChatButton);

      expect(onNewConversation).toHaveBeenCalled();
    });
  });
});
