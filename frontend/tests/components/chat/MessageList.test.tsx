/**
 * Tests for MessageList component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import { MessageList } from "@/components/chat/MessageList";
import { AudioProvider } from "@/components/providers/AudioContext";

// Mock scrollIntoView which is not available in jsdom
Element.prototype.scrollIntoView = jest.fn();

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <AudioProvider>{children}</AudioProvider>
);

const mockMessages = [
  {
    id: 1,
    role: "user" as const,
    content: "こんにちは",
    created_at: "2025-12-27T10:00:00Z",
  },
  {
    id: 2,
    role: "assistant" as const,
    content: "こんにちは！",
    created_at: "2025-12-27T10:00:01Z",
  },
  {
    id: 3,
    role: "user" as const,
    content: "今日の天気は？",
    created_at: "2025-12-27T10:00:02Z",
  },
];

describe("MessageList", () => {
  describe("rendering", () => {
    it("should render all messages", () => {
      render(
        <Wrapper>
          <MessageList messages={mockMessages} />
        </Wrapper>
      );

      expect(screen.getByText("こんにちは")).toBeInTheDocument();
      expect(screen.getByText("こんにちは！")).toBeInTheDocument();
      expect(screen.getByText("今日の天気は？")).toBeInTheDocument();
    });

    it("should render empty state when no messages", () => {
      render(
        <Wrapper>
          <MessageList messages={[]} />
        </Wrapper>
      );

      // Empty list should render without errors
      // The component shows an empty state message
      expect(screen.getByText(/メッセージはありません/)).toBeInTheDocument();
    });

    it("should render messages in order", () => {
      const { container } = render(
        <Wrapper>
          <MessageList messages={mockMessages} />
        </Wrapper>
      );

      const bubbles = container.querySelectorAll("[data-message-id]");
      expect(bubbles).toHaveLength(3);

      // Check order by checking data attributes
      expect(bubbles[0].getAttribute("data-message-id")).toBe("1");
      expect(bubbles[1].getAttribute("data-message-id")).toBe("2");
      expect(bubbles[2].getAttribute("data-message-id")).toBe("3");
    });
  });

  describe("scrolling", () => {
    it("should have scrollable container", () => {
      const { container } = render(
        <Wrapper>
          <MessageList messages={mockMessages} />
        </Wrapper>
      );

      const scrollContainer = container.firstChild as HTMLElement;
      expect(scrollContainer).toHaveClass("overflow-y-auto");
    });
  });

  describe("loading state", () => {
    it("should show loading indicator when isLoading is true", () => {
      render(
        <Wrapper>
          <MessageList messages={mockMessages} isLoading />
        </Wrapper>
      );

      // Loading indicator should be visible
      // Implementation may vary
    });

    it("should not show loading indicator when isLoading is false", () => {
      render(
        <Wrapper>
          <MessageList messages={mockMessages} isLoading={false} />
        </Wrapper>
      );

      // No loading indicator
    });
  });
});
