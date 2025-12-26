"use client";

import { useCallback } from "react";
import { useChatContext, chatActions } from "@/components/providers/ChatContext";
import type { Message } from "@/types/conversation";

/**
 * Hook for managing chat messages and sending state.
 */
export function useChat() {
  const { state, dispatch } = useChatContext();

  /**
   * Add a message to the current conversation.
   */
  const addMessage = useCallback(
    (message: Message) => {
      dispatch(chatActions.addMessage(message));
    },
    [dispatch]
  );

  /**
   * Set all messages for the current conversation.
   */
  const setMessages = useCallback(
    (messages: Message[]) => {
      dispatch(chatActions.setMessages(messages));
    },
    [dispatch]
  );

  /**
   * Clear all messages.
   */
  const clearMessages = useCallback(() => {
    dispatch(chatActions.setMessages([]));
  }, [dispatch]);

  /**
   * Set sending state.
   */
  const setSending = useCallback(
    (isSending: boolean) => {
      dispatch(chatActions.setSending(isSending));
    },
    [dispatch]
  );

  /**
   * Set error message.
   */
  const setError = useCallback(
    (error: string | null) => {
      dispatch(chatActions.setError(error));
    },
    [dispatch]
  );

  /**
   * Clear error message.
   */
  const clearError = useCallback(() => {
    dispatch(chatActions.clearError());
  }, [dispatch]);

  /**
   * Start a new conversation.
   */
  const newConversation = useCallback(() => {
    dispatch(chatActions.newConversation());
  }, [dispatch]);

  return {
    messages: state.messages,
    currentConversationId: state.currentConversationId,
    isSending: state.isSending,
    isLoading: state.isLoading,
    error: state.error,
    addMessage,
    setMessages,
    clearMessages,
    setSending,
    setError,
    clearError,
    newConversation,
  };
}
