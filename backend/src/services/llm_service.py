"""LLM Service for text response generation using OpenAI API."""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from src.models.llm import ErrorCode, LLMStatus, ServiceStatus, TokenUsage

if TYPE_CHECKING:
    from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Configuration constants
# fmt: off
SYSTEM_PROMPT = (
    "あなたは日本語の音声アシスタントです。以下のガイドラインに従ってください：\n\n"
    "1. 簡潔で自然な日本語で応答してください\n"
    "2. 音声で読み上げることを考慮し、長すぎる回答は避けてください\n"
    "3. 丁寧語（です・ます調）を使用してください\n"
    "4. 質問に対して正確かつ役立つ情報を提供してください\n"
    "5. 分からないことは正直に「分かりません」と答えてください\n\n"
    "応答は音声合成で読み上げられることを想定し、箇条書きや記号の使用は最小限にしてください。"
)
# fmt: on

MAX_MESSAGE_LENGTH = 4000
MAX_CONVERSATION_MESSAGES = 20
MAX_CONVERSATIONS = 1000
MAX_CONCURRENT_REQUESTS = 10
CONVERSATION_TTL_MINUTES = 60
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MAX_TOKENS = 1000


@dataclass
class Conversation:
    """Represents a conversation with message history."""

    id: str
    messages: list[dict[str, str]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class ConversationCache:
    """In-memory cache for conversation history with TTL cleanup."""

    def __init__(
        self,
        max_messages: int = MAX_CONVERSATION_MESSAGES,
        max_conversations: int = MAX_CONVERSATIONS,
        ttl_minutes: int = CONVERSATION_TTL_MINUTES,
    ) -> None:
        """Initialize conversation cache.

        Args:
            max_messages: Maximum messages per conversation
            max_conversations: Maximum number of conversations to cache
            ttl_minutes: Time-to-live in minutes for conversations
        """
        self._cache: dict[str, Conversation] = {}
        self._max_messages = max_messages
        self._max_conversations = max_conversations
        self._ttl = timedelta(minutes=ttl_minutes)

    def get_or_create(self, conversation_id: str) -> Conversation:
        """Get existing conversation or create new one.

        Args:
            conversation_id: Client-generated conversation ID

        Returns:
            Conversation object
        """
        self._cleanup_expired()
        if conversation_id not in self._cache:
            # Evict oldest conversations if at capacity
            self._evict_oldest_if_needed()
            self._cache[conversation_id] = Conversation(id=conversation_id)
            logger.debug("Created new conversation: %s", conversation_id)
        return self._cache[conversation_id]

    def add_message(
        self, conversation_id: str, role: str, content: str
    ) -> Conversation:
        """Add a message to a conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (user or assistant)
            content: Message content

        Returns:
            Updated conversation
        """
        conversation = self.get_or_create(conversation_id)
        conversation.messages.append({"role": role, "content": content})
        conversation.updated_at = datetime.now()

        # Trim oldest messages if exceeding limit
        if len(conversation.messages) > self._max_messages:
            trimmed = len(conversation.messages) - self._max_messages
            conversation.messages = conversation.messages[trimmed:]
            logger.debug(
                "Trimmed %d messages from conversation %s", trimmed, conversation_id
            )

        return conversation

    def clear(self, conversation_id: str) -> bool:
        """Clear a specific conversation.

        Args:
            conversation_id: Conversation ID to clear

        Returns:
            True if conversation existed and was cleared
        """
        if conversation_id in self._cache:
            del self._cache[conversation_id]
            logger.debug("Cleared conversation: %s", conversation_id)
            return True
        return False

    def count(self) -> int:
        """Return number of active conversations."""
        self._cleanup_expired()
        return len(self._cache)

    def _cleanup_expired(self) -> None:
        """Remove expired conversations."""
        now = datetime.now()
        expired = [k for k, v in self._cache.items() if now - v.updated_at > self._ttl]
        for k in expired:
            del self._cache[k]
        if expired:
            logger.debug("Cleaned up %d expired conversations", len(expired))

    def _evict_oldest_if_needed(self) -> None:
        """Evict oldest conversations if cache is at capacity."""
        if len(self._cache) >= self._max_conversations:
            # Sort by updated_at and remove oldest
            sorted_convs = sorted(self._cache.items(), key=lambda x: x[1].updated_at)
            to_evict = len(self._cache) - self._max_conversations + 1
            for conv_id, _ in sorted_convs[:to_evict]:
                del self._cache[conv_id]
            logger.debug(
                "Evicted %d oldest conversations (cache at capacity)", to_evict
            )


class LLMService:
    """Service for LLM text generation using OpenAI API."""

    def __init__(self) -> None:
        """Initialize LLM service."""
        self._client: AsyncOpenAI | None = None
        self._model = os.getenv("LLM_MODEL", DEFAULT_MODEL)
        self._max_tokens = int(os.getenv("LLM_MAX_TOKENS", str(DEFAULT_MAX_TOKENS)))
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._semaphore = asyncio.Semaphore(
            int(os.getenv("LLM_MAX_CONCURRENT", str(MAX_CONCURRENT_REQUESTS)))
        )
        self._conversation_cache = ConversationCache()
        self._last_check: datetime | None = None
        self._last_error: str | None = None

        if self._api_key:
            self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=self._api_key)
            logger.info("OpenAI client initialized with model: %s", self._model)
        except Exception as e:
            logger.exception("Failed to initialize OpenAI client")
            self._last_error = str(e)

    @property
    def api_configured(self) -> bool:
        """Check if API key is configured."""
        return self._api_key is not None and len(self._api_key) > 0

    async def generate_response(
        self, message: str, conversation_id: str
    ) -> tuple[str, TokenUsage | None]:
        """Generate LLM response for a message.

        Args:
            message: User's input message
            conversation_id: Client-generated conversation ID

        Returns:
            Tuple of (response text, token usage)

        Raises:
            ValueError: If message is invalid
            RuntimeError: If LLM API call fails
        """
        if not self.api_configured:
            raise RuntimeError(ErrorCode.LLM_NOT_CONFIGURED)

        if not message or not message.strip():
            raise ValueError(ErrorCode.EMPTY_MESSAGE)

        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(ErrorCode.MESSAGE_TOO_LONG)

        # Get conversation and add user message
        conversation = self._conversation_cache.add_message(
            conversation_id, "user", message
        )

        # Build messages for API call
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation.messages)

        async with self._semaphore:
            response_text, usage = await self._call_openai(messages)

        # Add assistant response to conversation
        self._conversation_cache.add_message(
            conversation_id, "assistant", response_text
        )

        return response_text, usage

    async def _call_openai(
        self, messages: list[dict[str, str]]
    ) -> tuple[str, TokenUsage | None]:
        """Call OpenAI API.

        Args:
            messages: List of messages for the API

        Returns:
            Tuple of (response text, token usage)
        """
        if self._client is None:
            raise RuntimeError(ErrorCode.LLM_NOT_CONFIGURED)

        try:
            from openai import (
                APIConnectionError,
                APIStatusError,
                AuthenticationError,
                RateLimitError,
            )

            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=self._max_tokens,
            )

            self._last_check = datetime.now()
            self._last_error = None

            text = response.choices[0].message.content or ""
            usage = None
            if response.usage:
                usage = TokenUsage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                )

            return text, usage

        except AuthenticationError as e:
            self._last_error = str(e)
            logger.error("OpenAI authentication error: %s", e)
            raise RuntimeError(ErrorCode.LLM_NOT_CONFIGURED) from e
        except RateLimitError as e:
            self._last_error = str(e)
            logger.warning("OpenAI rate limit: %s", e)
            raise RuntimeError(ErrorCode.LLM_RATE_LIMITED) from e
        except APIConnectionError as e:
            self._last_error = str(e)
            logger.error("OpenAI connection error: %s", e)
            raise RuntimeError(ErrorCode.LLM_CONNECTION_ERROR) from e
        except APIStatusError as e:
            self._last_error = str(e)
            logger.error("OpenAI API error: %s", e)
            raise RuntimeError(ErrorCode.LLM_API_ERROR) from e
        except Exception as e:
            self._last_error = str(e)
            logger.exception("Unexpected error calling OpenAI API")
            raise RuntimeError(ErrorCode.LLM_PROCESSING_ERROR) from e

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear a conversation's history.

        Args:
            conversation_id: Conversation ID to clear

        Returns:
            True if conversation was cleared
        """
        return self._conversation_cache.clear(conversation_id)

    def get_status(self) -> LLMStatus:
        """Get current service status.

        Returns:
            LLMStatus with service health information
        """
        if not self.api_configured:
            return LLMStatus(
                status=ServiceStatus.UNHEALTHY,
                model=self._model,
                api_configured=False,
                active_conversations=0,
                error_message="OPENAI_API_KEY environment variable not set",
            )

        if self._client is None:
            return LLMStatus(
                status=ServiceStatus.UNHEALTHY,
                model=self._model,
                api_configured=True,
                active_conversations=self._conversation_cache.count(),
                error_message=self._last_error or "OpenAI client not initialized",
            )

        status = ServiceStatus.HEALTHY
        if self._last_error:
            status = ServiceStatus.DEGRADED

        return LLMStatus(
            status=status,
            model=self._model,
            api_configured=True,
            active_conversations=self._conversation_cache.count(),
            last_check=self._last_check,
            error_message=self._last_error,
        )
