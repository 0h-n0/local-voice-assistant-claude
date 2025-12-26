/**
 * TypeScript types for conversation state and API responses.
 * Mirrors backend Pydantic models for type safety.
 */

// =============================================================================
// Message Types
// =============================================================================

/**
 * Message sender role.
 */
export type MessageRole = "user" | "assistant";

/**
 * Message in a conversation.
 */
export interface Message {
  id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

// =============================================================================
// Conversation Types
// =============================================================================

/**
 * Conversation summary for list view.
 */
export interface ConversationSummary {
  id: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * Full conversation with messages.
 */
export interface ConversationDetail {
  id: string;
  messages: Message[];
  created_at: string;
  updated_at: string;
}

/**
 * Paginated conversation list response.
 */
export interface ConversationListResponse {
  conversations: ConversationSummary[];
  total: number;
  limit: number;
  offset: number;
}

// =============================================================================
// Error Types
// =============================================================================

/**
 * Conversation error codes.
 */
export type ConversationErrorCode =
  | "CONVERSATION_NOT_FOUND"
  | "MESSAGE_TOO_LONG"
  | "DATABASE_ERROR";

/**
 * Conversation error response.
 */
export interface ConversationErrorResponse {
  error_code: ConversationErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

// =============================================================================
// Chat State Types (Frontend-specific)
// =============================================================================

/**
 * Global chat state managed by ChatContext.
 */
export interface ChatState {
  /** List of conversation summaries for sidebar */
  conversations: ConversationSummary[];

  /** Currently selected conversation ID */
  currentConversationId: string | null;

  /** Messages in current conversation */
  messages: Message[];

  /** Whether data is being loaded */
  isLoading: boolean;

  /** Whether a message is being sent/processed */
  isSending: boolean;

  /** Error message to display */
  error: string | null;
}

/**
 * Chat state actions.
 */
export type ChatAction =
  | { type: "SET_CONVERSATIONS"; payload: ConversationSummary[] }
  | { type: "ADD_CONVERSATION"; payload: ConversationSummary }
  | { type: "REMOVE_CONVERSATION"; payload: string }
  | { type: "UPDATE_CONVERSATION"; payload: ConversationSummary }
  | { type: "SELECT_CONVERSATION"; payload: string | null }
  | { type: "SET_MESSAGES"; payload: Message[] }
  | { type: "ADD_MESSAGE"; payload: Message }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_SENDING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "CLEAR_ERROR" }
  | { type: "NEW_CONVERSATION" };

/**
 * Initial chat state.
 */
export const initialChatState: ChatState = {
  conversations: [],
  currentConversationId: null,
  messages: [],
  isLoading: false,
  isSending: false,
  error: null,
};
