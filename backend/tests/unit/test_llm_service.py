"""Unit tests for LLM service."""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.llm import ErrorCode, ServiceStatus
from src.services.llm_service import (
    MAX_CONVERSATION_MESSAGES,
    MAX_MESSAGE_LENGTH,
    ConversationCache,
    LLMService,
)

# =============================================================================
# User Story 1: テキストプロンプトへの応答生成 (T011-T012)
# =============================================================================


class TestLLMServiceGenerateResponse:
    """Tests for LLMService.generate_response()."""

    @pytest.fixture
    def llm_service(self):
        """Create LLM service with mocked API key."""
        import importlib

        from src.models import config as config_module
        from src.services import llm_service as llm_module

        # Clear settings cache
        config_module.get_settings.cache_clear()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            # Reload config module to pick up new env vars
            importlib.reload(config_module)
            # Reload llm_service to use new settings
            importlib.reload(llm_module)
            service = llm_module.LLMService()
            yield service

        # Clean up - reload with original settings
        config_module.get_settings.cache_clear()
        importlib.reload(config_module)
        importlib.reload(llm_module)

    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "テスト応答です。"
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 20
        mock_response.usage.total_tokens = 120
        return mock_response

    async def test_generate_response_success(self, llm_service, mock_openai_response):
        """Test successful response generation."""
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        llm_service._client = mock_client

        text, usage = await llm_service.generate_response(
            "こんにちは", "test-conversation-1"
        )

        assert text == "テスト応答です。"
        assert usage is not None
        assert usage.prompt_tokens == 100
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 120

    async def test_generate_response_empty_message_raises_error(self, llm_service):
        """Test that empty message raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await llm_service.generate_response("", "test-conversation")

        assert ErrorCode.EMPTY_MESSAGE in str(exc_info.value)

    async def test_generate_response_whitespace_message_raises_error(self, llm_service):
        """Test that whitespace-only message raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await llm_service.generate_response("   ", "test-conversation")

        assert ErrorCode.EMPTY_MESSAGE in str(exc_info.value)

    async def test_generate_response_too_long_message_raises_error(self, llm_service):
        """Test that message exceeding limit raises ValueError."""
        long_message = "あ" * (MAX_MESSAGE_LENGTH + 1)

        with pytest.raises(ValueError) as exc_info:
            await llm_service.generate_response(long_message, "test-conversation")

        assert ErrorCode.MESSAGE_TOO_LONG in str(exc_info.value)

    async def test_generate_response_max_length_message_succeeds(
        self, llm_service, mock_openai_response
    ):
        """Test that message at exactly max length succeeds."""
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        llm_service._client = mock_client

        max_message = "あ" * MAX_MESSAGE_LENGTH
        text, usage = await llm_service.generate_response(max_message, "test-conv")

        assert text == "テスト応答です。"

    async def test_generate_response_no_api_key_raises_error(self):
        """Test that missing API key raises RuntimeError."""
        with patch.dict("os.environ", {}, clear=True):
            service = LLMService()

            with pytest.raises(RuntimeError) as exc_info:
                await service.generate_response("test", "test-conv")

            assert ErrorCode.LLM_NOT_CONFIGURED in str(exc_info.value)


class TestInputValidation:
    """Tests for input validation (T012)."""

    def test_message_length_validation_boundary(self):
        """Test message length at boundary conditions."""
        # Exactly at limit should be valid
        valid_message = "a" * MAX_MESSAGE_LENGTH
        assert len(valid_message) == MAX_MESSAGE_LENGTH

        # Over limit should be invalid
        invalid_message = "a" * (MAX_MESSAGE_LENGTH + 1)
        assert len(invalid_message) > MAX_MESSAGE_LENGTH


# =============================================================================
# User Story 2: 会話コンテキストの維持 (T025-T027)
# =============================================================================


class TestConversationCache:
    """Tests for ConversationCache class."""

    def test_get_or_create_new_conversation(self):
        """Test creating a new conversation."""
        cache = ConversationCache()
        conv = cache.get_or_create("test-id")

        assert conv.id == "test-id"
        assert conv.messages == []
        assert isinstance(conv.created_at, datetime)

    def test_get_or_create_existing_conversation(self):
        """Test getting existing conversation."""
        cache = ConversationCache()
        conv1 = cache.get_or_create("test-id")
        conv1.messages.append({"role": "user", "content": "hello"})

        conv2 = cache.get_or_create("test-id")

        assert conv2 is conv1
        assert len(conv2.messages) == 1

    def test_add_message_to_conversation(self):
        """Test adding messages to conversation."""
        cache = ConversationCache()
        cache.add_message("test-id", "user", "Hello")
        cache.add_message("test-id", "assistant", "Hi there")

        conv = cache.get_or_create("test-id")
        assert len(conv.messages) == 2
        assert conv.messages[0]["role"] == "user"
        assert conv.messages[1]["role"] == "assistant"

    def test_message_limit_enforcement(self):
        """Test that oldest messages are trimmed when limit exceeded."""
        cache = ConversationCache(max_messages=5)

        # Add 7 messages
        for i in range(7):
            cache.add_message("test-id", "user", f"Message {i}")

        conv = cache.get_or_create("test-id")
        assert len(conv.messages) == 5
        # Oldest messages should be trimmed
        assert conv.messages[0]["content"] == "Message 2"
        assert conv.messages[-1]["content"] == "Message 6"

    def test_message_limit_at_max_conversations(self):
        """Test exactly at max message limit."""
        cache = ConversationCache(max_messages=MAX_CONVERSATION_MESSAGES)

        for i in range(MAX_CONVERSATION_MESSAGES):
            cache.add_message("test-id", "user", f"Message {i}")

        conv = cache.get_or_create("test-id")
        assert len(conv.messages) == MAX_CONVERSATION_MESSAGES

    def test_ttl_expiration(self):
        """Test that expired conversations are cleaned up."""
        cache = ConversationCache(ttl_minutes=1)

        # Create a conversation
        conv = cache.get_or_create("test-id")

        # Manually set updated_at to past
        conv.updated_at = datetime.now() - timedelta(minutes=2)

        # Access should trigger cleanup
        new_conv = cache.get_or_create("test-id")

        # Should be a new conversation (old one expired)
        assert new_conv.messages == []
        assert new_conv.updated_at > conv.updated_at

    def test_clear_conversation(self):
        """Test clearing a specific conversation."""
        cache = ConversationCache()
        cache.add_message("test-id", "user", "Hello")

        result = cache.clear("test-id")
        assert result is True
        assert cache.count() == 0

    def test_clear_nonexistent_conversation(self):
        """Test clearing a conversation that doesn't exist."""
        cache = ConversationCache()
        result = cache.clear("nonexistent")
        assert result is False

    def test_count_conversations(self):
        """Test counting active conversations."""
        cache = ConversationCache()
        cache.add_message("conv-1", "user", "Hello")
        cache.add_message("conv-2", "user", "Hi")

        assert cache.count() == 2

    def test_cache_eviction_at_capacity(self):
        """Test that oldest conversations are evicted when cache is at capacity."""
        cache = ConversationCache(max_conversations=3)

        # Add 3 conversations
        cache.add_message("conv-1", "user", "First")
        cache.add_message("conv-2", "user", "Second")
        cache.add_message("conv-3", "user", "Third")

        assert cache.count() == 3

        # Add a 4th conversation - oldest (conv-1) should be evicted
        cache.add_message("conv-4", "user", "Fourth")

        assert cache.count() == 3
        # conv-1 should be evicted
        conv = cache.get_or_create("conv-1")
        assert conv.messages == []  # New conversation, not the old one


# =============================================================================
# User Story 3: サービス健全性の確認 (T037)
# =============================================================================


class TestLLMServiceStatus:
    """Tests for LLMService.get_status()."""

    def test_status_healthy_with_api_key(self) -> None:
        """Test healthy status when API key is configured."""
        import importlib

        from src.models import config as config_module
        from src.services import llm_service as llm_module

        config_module.get_settings.cache_clear()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            importlib.reload(config_module)
            importlib.reload(llm_module)
            service = llm_module.LLMService()
            status = service.get_status()

            assert status.status == ServiceStatus.HEALTHY
            assert status.api_configured is True
            assert status.model == "gpt-4o-mini"

        config_module.get_settings.cache_clear()
        importlib.reload(config_module)
        importlib.reload(llm_module)

    def test_status_unhealthy_no_api_key(self) -> None:
        """Test unhealthy status when API key is missing."""
        import importlib

        from src.models import config as config_module
        from src.services import llm_service as llm_module

        config_module.get_settings.cache_clear()

        with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
            importlib.reload(config_module)
            importlib.reload(llm_module)
            service = llm_module.LLMService()
            status = service.get_status()

            assert status.status == ServiceStatus.UNHEALTHY
            assert status.api_configured is False
            assert "OPENAI_API_KEY" in (status.error_message or "")

        config_module.get_settings.cache_clear()
        importlib.reload(config_module)
        importlib.reload(llm_module)

    def test_status_tracks_active_conversations(self) -> None:
        """Test that status includes active conversation count."""
        import importlib

        from src.models import config as config_module
        from src.services import llm_service as llm_module

        config_module.get_settings.cache_clear()

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
            importlib.reload(config_module)
            importlib.reload(llm_module)
            service = llm_module.LLMService()
            # Add some conversations manually
            service._conversation_cache.add_message("conv-1", "user", "hello")
            service._conversation_cache.add_message("conv-2", "user", "hi")

            status = service.get_status()

            assert status.active_conversations == 2

        config_module.get_settings.cache_clear()
        importlib.reload(config_module)
        importlib.reload(llm_module)
