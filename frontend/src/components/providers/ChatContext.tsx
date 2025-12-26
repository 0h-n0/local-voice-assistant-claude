"use client";

import {
  createContext,
  useContext,
  useReducer,
  type ReactNode,
  type Dispatch,
} from "react";
import {
  type ChatState,
  type ChatAction,
  initialChatState,
} from "@/types/conversation";

// =============================================================================
// Chat Reducer
// =============================================================================

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "SET_CONVERSATIONS":
      return {
        ...state,
        conversations: action.payload,
      };

    case "ADD_CONVERSATION":
      return {
        ...state,
        conversations: [action.payload, ...state.conversations],
      };

    case "REMOVE_CONVERSATION":
      return {
        ...state,
        conversations: state.conversations.filter(
          (conv) => conv.id !== action.payload
        ),
        // Clear current conversation if it was the deleted one
        currentConversationId:
          state.currentConversationId === action.payload
            ? null
            : state.currentConversationId,
        messages:
          state.currentConversationId === action.payload ? [] : state.messages,
      };

    case "UPDATE_CONVERSATION":
      return {
        ...state,
        conversations: state.conversations.map((conv) =>
          conv.id === action.payload.id ? action.payload : conv
        ),
      };

    case "SELECT_CONVERSATION":
      return {
        ...state,
        currentConversationId: action.payload,
        // Clear messages when selecting a new conversation (will be loaded separately)
        messages: action.payload === null ? [] : state.messages,
      };

    case "SET_MESSAGES":
      return {
        ...state,
        messages: action.payload,
      };

    case "ADD_MESSAGE":
      return {
        ...state,
        messages: [...state.messages, action.payload],
      };

    case "SET_LOADING":
      return {
        ...state,
        isLoading: action.payload,
      };

    case "SET_SENDING":
      return {
        ...state,
        isSending: action.payload,
      };

    case "SET_ERROR":
      return {
        ...state,
        error: action.payload,
      };

    case "CLEAR_ERROR":
      return {
        ...state,
        error: null,
      };

    case "NEW_CONVERSATION":
      return {
        ...state,
        currentConversationId: null,
        messages: [],
        error: null,
      };

    default:
      return state;
  }
}

// =============================================================================
// Context Definition
// =============================================================================

interface ChatContextValue {
  state: ChatState;
  dispatch: Dispatch<ChatAction>;
}

const ChatContext = createContext<ChatContextValue | null>(null);

// =============================================================================
// Provider Component
// =============================================================================

interface ChatProviderProps {
  children: ReactNode;
}

export function ChatProvider({ children }: ChatProviderProps) {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);

  return (
    <ChatContext.Provider value={{ state, dispatch }}>
      {children}
    </ChatContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

export function useChatContext(): ChatContextValue {
  const context = useContext(ChatContext);

  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }

  return context;
}

// =============================================================================
// Action Creators (convenience functions)
// =============================================================================

export const chatActions = {
  setConversations: (
    conversations: ChatState["conversations"]
  ): ChatAction => ({
    type: "SET_CONVERSATIONS",
    payload: conversations,
  }),

  addConversation: (
    conversation: ChatState["conversations"][0]
  ): ChatAction => ({
    type: "ADD_CONVERSATION",
    payload: conversation,
  }),

  removeConversation: (id: string): ChatAction => ({
    type: "REMOVE_CONVERSATION",
    payload: id,
  }),

  updateConversation: (
    conversation: ChatState["conversations"][0]
  ): ChatAction => ({
    type: "UPDATE_CONVERSATION",
    payload: conversation,
  }),

  selectConversation: (id: string | null): ChatAction => ({
    type: "SELECT_CONVERSATION",
    payload: id,
  }),

  setMessages: (messages: ChatState["messages"]): ChatAction => ({
    type: "SET_MESSAGES",
    payload: messages,
  }),

  addMessage: (message: ChatState["messages"][0]): ChatAction => ({
    type: "ADD_MESSAGE",
    payload: message,
  }),

  setLoading: (isLoading: boolean): ChatAction => ({
    type: "SET_LOADING",
    payload: isLoading,
  }),

  setSending: (isSending: boolean): ChatAction => ({
    type: "SET_SENDING",
    payload: isSending,
  }),

  setError: (error: string | null): ChatAction => ({
    type: "SET_ERROR",
    payload: error,
  }),

  clearError: (): ChatAction => ({
    type: "CLEAR_ERROR",
  }),

  newConversation: (): ChatAction => ({
    type: "NEW_CONVERSATION",
  }),
};
