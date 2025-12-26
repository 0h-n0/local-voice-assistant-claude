"use client";

import type { Message } from "@/types/conversation";

interface MessageBubbleProps {
  message: Message;
  showTimestamp?: boolean;
  onReplay?: (messageId: number, content: string) => void;
  isPlaying?: boolean;
  className?: string;
}

/**
 * Message bubble component for displaying a single chat message.
 * User messages are on the right (blue), assistant messages are on the left (gray).
 */
export function MessageBubble({
  message,
  showTimestamp = false,
  onReplay,
  isPlaying = false,
  className = "",
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  const formatTimestamp = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("ja-JP", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} ${className}`}
      data-message-id={message.id}
    >
      <div className="max-w-[80%]">
        {/* Message bubble */}
        <div
          data-role={message.role}
          data-selected={false}
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? "bg-blue-500 text-white"
              : "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-100"
          }`}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {/* Footer with timestamp and replay button */}
        <div
          className={`mt-1 flex items-center gap-2 ${
            isUser ? "justify-end" : "justify-start"
          }`}
        >
          {/* Timestamp */}
          {showTimestamp && (
            <time
              dateTime={message.created_at}
              className="text-xs text-zinc-400 dark:text-zinc-500"
            >
              {formatTimestamp(message.created_at)}
            </time>
          )}

          {/* Replay button for assistant messages */}
          {!isUser && onReplay && (
            <button
              type="button"
              onClick={() => onReplay(message.id, message.content)}
              disabled={isPlaying}
              className={`flex items-center gap-1 text-xs transition-colors ${
                isPlaying
                  ? "text-blue-500"
                  : "text-zinc-400 hover:text-zinc-600 dark:text-zinc-500 dark:hover:text-zinc-300"
              }`}
              aria-label={isPlaying ? "再生中" : "再生"}
            >
              {isPlaying ? (
                <PlayingIcon className="h-3 w-3" />
              ) : (
                <ReplayIcon className="h-3 w-3" />
              )}
              <span>{isPlaying ? "再生中" : "再生"}</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Icons
// =============================================================================

function ReplayIcon({ className = "" }: { className?: string }) {
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
        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
      />
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </svg>
  );
}

function PlayingIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={`animate-pulse ${className}`}
      fill="currentColor"
      viewBox="0 0 24 24"
    >
      <path d="M9 8h2v8H9V8zm4 0h2v8h-2V8z" />
    </svg>
  );
}
