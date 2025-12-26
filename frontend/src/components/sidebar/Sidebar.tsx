"use client";

import { useEffect } from "react";
import { ConversationList } from "./ConversationList";
import { useConversations } from "@/hooks/useConversations";
import { useChat } from "@/hooks/useChat";

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  onNewConversation?: () => void;
  className?: string;
}

/**
 * Sidebar component with conversation history list.
 * Mobile responsive with slide-in animation.
 */
export function Sidebar({
  isOpen = true,
  onClose,
  onNewConversation,
  className = "",
}: SidebarProps) {
  const {
    conversations,
    currentConversationId,
    isLoading,
    fetchConversations,
    selectConversation,
    deleteConversation,
  } = useConversations();

  const { newConversation } = useChat();

  // Fetch conversations on mount
  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  const handleNewConversation = () => {
    newConversation();
    onNewConversation?.();
  };

  const handleSelectConversation = async (conversationId: string) => {
    await selectConversation(conversationId);
    // Close sidebar on mobile after selection
    onClose?.();
  };

  const handleDeleteConversation = async (conversationId: string) => {
    await deleteConversation(conversationId);
  };

  return (
    <aside
      className={`
        flex h-full w-64 flex-col border-r border-zinc-200 bg-zinc-50 transition-transform dark:border-zinc-700 dark:bg-zinc-900
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
        ${className}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-200 p-4 dark:border-zinc-700">
        <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100">
          会話履歴
        </h2>
        {onClose && (
          <button
            type="button"
            onClick={onClose}
            className="rounded p-1 text-zinc-500 hover:bg-zinc-200 dark:hover:bg-zinc-700"
            aria-label="閉じる"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* New Conversation Button */}
      <div className="p-2">
        <button
          type="button"
          onClick={handleNewConversation}
          className="flex w-full items-center justify-center gap-2 rounded-lg border border-zinc-300 bg-white px-4 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-100 dark:border-zinc-600 dark:bg-zinc-800 dark:text-zinc-200 dark:hover:bg-zinc-700"
        >
          <PlusIcon className="h-4 w-4" />
          新しいチャット
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2">
        <ConversationList
          conversations={conversations}
          selectedId={currentConversationId}
          isLoading={isLoading}
          onSelect={handleSelectConversation}
          onDelete={handleDeleteConversation}
        />
      </div>
    </aside>
  );
}

// =============================================================================
// Icons
// =============================================================================

function CloseIcon({ className = "" }: { className?: string }) {
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
        d="M6 18L18 6M6 6l12 12"
      />
    </svg>
  );
}

function PlusIcon({ className = "" }: { className?: string }) {
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
        d="M12 4v16m8-8H4"
      />
    </svg>
  );
}
