"use client";

import { useEffect, useRef } from "react";
import { MessageBubble } from "./MessageBubble";
import type { Message } from "@/types/conversation";

interface MessageListProps {
  messages: Message[];
  isLoading?: boolean;
  showTimestamps?: boolean;
  onReplay?: (messageId: number, content: string) => void;
  currentPlayingMessageId?: number | null;
  className?: string;
}

/**
 * Scrollable list of chat messages with auto-scroll to bottom.
 */
export function MessageList({
  messages,
  isLoading = false,
  showTimestamps = true,
  onReplay,
  currentPlayingMessageId,
  className = "",
}: MessageListProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages.length]);

  return (
    <div
      ref={containerRef}
      className={`flex-1 overflow-y-auto ${className}`}
      role="log"
      aria-live="polite"
    >
      {messages.length === 0 && !isLoading ? (
        <div className="flex h-full items-center justify-center">
          <p className="text-zinc-400 dark:text-zinc-500">
            メッセージはありません
          </p>
        </div>
      ) : (
        <div className="space-y-4 p-4">
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              showTimestamp={showTimestamps}
              onReplay={onReplay}
              isPlaying={currentPlayingMessageId === message.id}
            />
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg bg-zinc-100 px-4 py-2 dark:bg-zinc-800">
                <div className="flex items-center gap-2">
                  <LoadingDots />
                  <span className="text-sm text-zinc-500">処理中...</span>
                </div>
              </div>
            </div>
          )}

          {/* Scroll anchor */}
          <div ref={bottomRef} />
        </div>
      )}
    </div>
  );
}

/**
 * Animated loading dots.
 */
function LoadingDots() {
  return (
    <div className="flex gap-1">
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
    </div>
  );
}
