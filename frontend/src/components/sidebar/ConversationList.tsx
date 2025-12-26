"use client";

import type { ConversationSummary } from "@/types/conversation";
import { LoadingSpinner, TrashIcon } from "@/components/shared/Icons";

interface ConversationListProps {
  conversations: ConversationSummary[];
  selectedId?: string | null;
  isLoading?: boolean;
  onSelect: (conversationId: string) => void;
  onDelete?: (conversationId: string) => void;
  className?: string;
}

/**
 * List of conversations with selection and deletion support.
 */
export function ConversationList({
  conversations,
  selectedId,
  isLoading = false,
  onSelect,
  onDelete,
  className = "",
}: ConversationListProps) {
  const formatDate = (isoString: string): string => {
    const date = new Date(isoString);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24)
    );

    if (diffDays === 0) {
      return date.toLocaleTimeString("ja-JP", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (diffDays === 1) {
      return "昨日";
    } else if (diffDays < 7) {
      return `${diffDays}日前`;
    } else {
      return date.toLocaleDateString("ja-JP", {
        month: "short",
        day: "numeric",
      });
    }
  };

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center p-4 ${className}`}>
        <div className="flex items-center gap-2 text-zinc-500">
          <LoadingSpinner />
          <span>読み込み中...</span>
        </div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className={`flex items-center justify-center p-4 ${className}`}>
        <p className="text-zinc-400 dark:text-zinc-500">
          会話履歴がありません
        </p>
      </div>
    );
  }

  return (
    <div className={`space-y-1 ${className}`}>
      {conversations.map((conversation) => {
        const isSelected = selectedId === conversation.id;

        return (
          <div
            key={conversation.id}
            data-testid={`conversation-${conversation.id}`}
            data-selected={isSelected}
            className="group relative"
          >
            <button
              type="button"
              onClick={() => onSelect(conversation.id)}
              className={`w-full rounded-lg px-3 py-2 text-left transition-colors ${
                isSelected
                  ? "bg-blue-50 dark:bg-blue-900/30"
                  : "hover:bg-zinc-100 dark:hover:bg-zinc-800"
              }`}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`text-sm font-medium ${
                    isSelected
                      ? "text-blue-600 dark:text-blue-400"
                      : "text-zinc-900 dark:text-zinc-100"
                  }`}
                >
                  会話 {conversation.id.slice(0, 8)}
                </span>
                <span className="text-xs text-zinc-400 dark:text-zinc-500">
                  {formatDate(conversation.updated_at)}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs text-zinc-500 dark:text-zinc-400">
                  {conversation.message_count} メッセージ
                </span>
              </div>
            </button>

            {/* Delete button */}
            {onDelete && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(conversation.id);
                }}
                className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-zinc-400 opacity-0 transition-opacity hover:bg-red-100 hover:text-red-600 group-hover:opacity-100 dark:hover:bg-red-900/30 dark:hover:text-red-400"
                aria-label="削除"
              >
                <TrashIcon className="h-4 w-4" />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
