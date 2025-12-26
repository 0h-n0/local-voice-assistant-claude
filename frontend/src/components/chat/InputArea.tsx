"use client";

import { useState, useCallback, type KeyboardEvent } from "react";

interface InputAreaProps {
  /** Callback when message is submitted */
  onSend: (message: string) => void;
  /** Whether the input is disabled */
  disabled?: boolean;
  /** Whether voice recording is active (visual indicator) */
  isRecording?: boolean;
  /** Placeholder text */
  placeholder?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Text input area with send button for chat messages.
 * Supports Enter key to send (Shift+Enter for newline).
 */
export function InputArea({
  onSend,
  disabled = false,
  isRecording = false,
  placeholder = "メッセージを入力...",
  className = "",
}: InputAreaProps) {
  const [value, setValue] = useState("");

  const handleSend = useCallback(() => {
    const trimmedValue = value.trim();
    if (trimmedValue && !disabled) {
      onSend(trimmedValue);
      setValue("");
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter" && !e.shiftKey && !disabled) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend, disabled]
  );

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={placeholder}
        className={`flex-1 rounded-lg border px-4 py-2 transition-colors ${
          disabled
            ? "cursor-not-allowed border-zinc-200 bg-zinc-100 text-zinc-400 dark:border-zinc-700 dark:bg-zinc-800"
            : "border-zinc-300 bg-white focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:border-zinc-600 dark:bg-zinc-900 dark:text-zinc-100"
        } ${isRecording ? "border-red-300 dark:border-red-700" : ""}`}
      />
      <button
        type="button"
        onClick={handleSend}
        disabled={!canSend}
        className={`flex h-10 w-10 items-center justify-center rounded-lg transition-colors ${
          canSend
            ? "bg-blue-500 text-white hover:bg-blue-600"
            : "cursor-not-allowed bg-zinc-200 text-zinc-400 dark:bg-zinc-700 dark:text-zinc-500"
        }`}
        aria-label="送信"
      >
        <SendIcon className="h-5 w-5" />
      </button>
    </div>
  );
}

// =============================================================================
// Icons
// =============================================================================

function SendIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      fill="none"
      viewBox="0 0 24 24"
      stroke="currentColor"
      strokeWidth={2}
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
      />
    </svg>
  );
}
