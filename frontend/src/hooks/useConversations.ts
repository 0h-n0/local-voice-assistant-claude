"use client";

import { useCallback } from "react";
import { useChatContext, chatActions } from "@/components/providers/ChatContext";
import { getConversations, getConversation, deleteConversation as apiDeleteConversation } from "@/lib/api";

/**
 * Hook for managing conversations list and selection.
 */
export function useConversations() {
  const { state, dispatch } = useChatContext();

  /**
   * Fetch list of conversations from API.
   */
  const fetchConversations = useCallback(
    async (limit = 20, offset = 0) => {
      dispatch(chatActions.setLoading(true));
      dispatch(chatActions.clearError());

      try {
        const response = await getConversations(limit, offset);
        dispatch(chatActions.setConversations(response.conversations));
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "会話履歴の取得に失敗しました";
        dispatch(chatActions.setError(errorMessage));
      } finally {
        dispatch(chatActions.setLoading(false));
      }
    },
    [dispatch]
  );

  /**
   * Select a conversation and fetch its messages.
   */
  const selectConversation = useCallback(
    async (conversationId: string) => {
      dispatch(chatActions.setLoading(true));
      dispatch(chatActions.clearError());
      dispatch(chatActions.selectConversation(conversationId));

      try {
        const conversation = await getConversation(conversationId);
        dispatch(chatActions.setMessages(conversation.messages));
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "会話の取得に失敗しました";
        dispatch(chatActions.setError(errorMessage));
      } finally {
        dispatch(chatActions.setLoading(false));
      }
    },
    [dispatch]
  );

  /**
   * Delete a conversation.
   */
  const deleteConversation = useCallback(
    async (conversationId: string) => {
      try {
        await apiDeleteConversation(conversationId);
        dispatch(chatActions.removeConversation(conversationId));
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : "会話の削除に失敗しました";
        dispatch(chatActions.setError(errorMessage));
      }
    },
    [dispatch]
  );

  /**
   * Clear current conversation selection.
   */
  const clearSelection = useCallback(() => {
    dispatch(chatActions.selectConversation(null));
    dispatch(chatActions.setMessages([]));
  }, [dispatch]);

  /**
   * Refresh conversation list.
   */
  const refreshConversations = useCallback(async () => {
    await fetchConversations();
  }, [fetchConversations]);

  return {
    conversations: state.conversations,
    currentConversationId: state.currentConversationId,
    isLoading: state.isLoading,
    error: state.error,
    fetchConversations,
    selectConversation,
    deleteConversation,
    clearSelection,
    refreshConversations,
  };
}
