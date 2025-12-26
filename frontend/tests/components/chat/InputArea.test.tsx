/**
 * Tests for InputArea component.
 * @jest-environment jsdom
 */

import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { InputArea } from "@/components/chat/InputArea";

describe("InputArea", () => {
  const onSend = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("rendering", () => {
    it("should render input field and send button", () => {
      render(<InputArea onSend={onSend} />);

      expect(
        screen.getByPlaceholderText(/メッセージを入力/i)
      ).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /送信/i })
      ).toBeInTheDocument();
    });

    it("should disable send button when input is empty", () => {
      render(<InputArea onSend={onSend} />);

      const sendButton = screen.getByRole("button", { name: /送信/i });
      expect(sendButton).toBeDisabled();
    });

    it("should enable send button when input has text", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "テストメッセージ" } });

      const sendButton = screen.getByRole("button", { name: /送信/i });
      expect(sendButton).not.toBeDisabled();
    });
  });

  describe("sending messages", () => {
    it("should call onSend when send button is clicked", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "テストメッセージ" } });

      const sendButton = screen.getByRole("button", { name: /送信/i });
      fireEvent.click(sendButton);

      expect(onSend).toHaveBeenCalledWith("テストメッセージ");
    });

    it("should call onSend when Enter key is pressed", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "テストメッセージ" } });
      fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

      expect(onSend).toHaveBeenCalledWith("テストメッセージ");
    });

    it("should not send when Shift+Enter is pressed", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "テストメッセージ" } });
      fireEvent.keyDown(input, { key: "Enter", code: "Enter", shiftKey: true });

      expect(onSend).not.toHaveBeenCalled();
    });

    it("should clear input after sending", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(
        /メッセージを入力/i
      ) as HTMLInputElement;
      fireEvent.change(input, { target: { value: "テストメッセージ" } });
      fireEvent.click(screen.getByRole("button", { name: /送信/i }));

      expect(input.value).toBe("");
    });

    it("should trim whitespace before sending", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "  テストメッセージ  " } });
      fireEvent.click(screen.getByRole("button", { name: /送信/i }));

      expect(onSend).toHaveBeenCalledWith("テストメッセージ");
    });

    it("should not send empty message after trimming", () => {
      render(<InputArea onSend={onSend} />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "   " } });
      fireEvent.click(screen.getByRole("button", { name: /送信/i }));

      expect(onSend).not.toHaveBeenCalled();
    });
  });

  describe("disabled state", () => {
    it("should disable input when disabled prop is true", () => {
      render(<InputArea onSend={onSend} disabled />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      expect(input).toBeDisabled();
    });

    it("should disable send button when disabled prop is true", () => {
      render(<InputArea onSend={onSend} disabled />);

      const sendButton = screen.getByRole("button", { name: /送信/i });
      expect(sendButton).toBeDisabled();
    });

    it("should not call onSend when disabled", () => {
      render(<InputArea onSend={onSend} disabled />);

      const input = screen.getByPlaceholderText(/メッセージを入力/i);
      fireEvent.change(input, { target: { value: "テストメッセージ" } });
      fireEvent.keyDown(input, { key: "Enter", code: "Enter" });

      expect(onSend).not.toHaveBeenCalled();
    });
  });

  describe("integration with voice recording", () => {
    it("should preserve input value when isRecording changes", () => {
      const { rerender } = render(
        <InputArea onSend={onSend} isRecording={false} />
      );

      const input = screen.getByPlaceholderText(
        /メッセージを入力/i
      ) as HTMLInputElement;
      fireEvent.change(input, { target: { value: "保存されるテキスト" } });

      // Simulate recording starting
      rerender(<InputArea onSend={onSend} isRecording={true} />);

      // Input value should be preserved
      expect(input.value).toBe("保存されるテキスト");
    });
  });
});
