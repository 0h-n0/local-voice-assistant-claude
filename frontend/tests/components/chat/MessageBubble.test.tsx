/**
 * Tests for MessageBubble component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen } from "@testing-library/react";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { AudioProvider } from "@/components/providers/AudioContext";

const Wrapper = ({ children }: { children: React.ReactNode }) => (
  <AudioProvider>{children}</AudioProvider>
);

describe("MessageBubble", () => {
  const userMessage = {
    id: 1,
    role: "user" as const,
    content: "こんにちは",
    created_at: "2025-12-27T10:00:00Z",
  };

  const assistantMessage = {
    id: 2,
    role: "assistant" as const,
    content: "こんにちは！お手伝いできることはありますか？",
    created_at: "2025-12-27T10:00:01Z",
  };

  describe("user message", () => {
    it("should render message content", () => {
      render(
        <Wrapper>
          <MessageBubble message={userMessage} />
        </Wrapper>
      );

      expect(screen.getByText("こんにちは")).toBeInTheDocument();
    });

    it("should have blue background for user messages", () => {
      const { container } = render(
        <Wrapper>
          <MessageBubble message={userMessage} />
        </Wrapper>
      );

      const bubble = container.querySelector("[data-role='user']");
      expect(bubble).toBeInTheDocument();
    });

    it("should be aligned to the right", () => {
      const { container } = render(
        <Wrapper>
          <MessageBubble message={userMessage} />
        </Wrapper>
      );

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass("justify-end");
    });
  });

  describe("assistant message", () => {
    it("should render message content", () => {
      render(
        <Wrapper>
          <MessageBubble message={assistantMessage} />
        </Wrapper>
      );

      expect(
        screen.getByText("こんにちは！お手伝いできることはありますか？")
      ).toBeInTheDocument();
    });

    it("should have gray background for assistant messages", () => {
      const { container } = render(
        <Wrapper>
          <MessageBubble message={assistantMessage} />
        </Wrapper>
      );

      const bubble = container.querySelector("[data-role='assistant']");
      expect(bubble).toBeInTheDocument();
    });

    it("should be aligned to the left", () => {
      const { container } = render(
        <Wrapper>
          <MessageBubble message={assistantMessage} />
        </Wrapper>
      );

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass("justify-start");
    });
  });

  describe("timestamp", () => {
    it("should display timestamp when showTimestamp is true", () => {
      render(
        <Wrapper>
          <MessageBubble message={userMessage} showTimestamp />
        </Wrapper>
      );

      // Timestamp should be visible
      const timeElement = screen.getByRole("time");
      expect(timeElement).toBeInTheDocument();
    });

    it("should not display timestamp when showTimestamp is false", () => {
      render(
        <Wrapper>
          <MessageBubble message={userMessage} showTimestamp={false} />
        </Wrapper>
      );

      // Timestamp should not be visible
      const timeElement = screen.queryByRole("time");
      expect(timeElement).not.toBeInTheDocument();
    });
  });
});
