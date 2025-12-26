"""Integration tests for LLM API endpoints."""

import importlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.dependencies import set_llm_service
from src.main import app
from src.models.llm import ErrorCode


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "テスト応答です。"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 100
    mock_response.usage.completion_tokens = 20
    mock_response.usage.total_tokens = 120
    return mock_response


@pytest.fixture
def llm_service_with_mock(mock_openai_response):
    """Create LLM service with mocked OpenAI client."""
    from src.models import config as config_module
    from src.services import llm_service as llm_module

    config_module.get_settings.cache_clear()

    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}, clear=False):
        importlib.reload(config_module)
        importlib.reload(llm_module)
        service = llm_module.LLMService()
        mock_client = AsyncMock()
        mock_client.chat.completions.create = AsyncMock(
            return_value=mock_openai_response
        )
        service._client = mock_client
        set_llm_service(service)
        yield service

    config_module.get_settings.cache_clear()
    importlib.reload(config_module)
    importlib.reload(llm_module)


@pytest.fixture
def llm_service_unconfigured():
    """Create LLM service without API key."""
    from src.models import config as config_module
    from src.services import llm_service as llm_module

    config_module.get_settings.cache_clear()

    with patch.dict("os.environ", {"OPENAI_API_KEY": ""}, clear=False):
        importlib.reload(config_module)
        importlib.reload(llm_module)
        service = llm_module.LLMService()
        set_llm_service(service)
        yield service

    config_module.get_settings.cache_clear()
    importlib.reload(config_module)
    importlib.reload(llm_module)


# =============================================================================
# User Story 1: テキストプロンプトへの応答生成 (T013-T014)
# =============================================================================


class TestChatEndpoint:
    """Integration tests for POST /api/llm/chat."""

    async def test_chat_success(self, llm_service_with_mock):
        """Test successful chat request."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "こんにちは", "conversation_id": "test-conv-1"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "テスト応答です。"
        assert data["conversation_id"] == "test-conv-1"
        assert data["usage"]["total_tokens"] == 120
        assert data["processing_time_seconds"] >= 0

    async def test_chat_empty_message_returns_422(self, llm_service_with_mock):
        """Test that empty message returns 422 validation error."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "", "conversation_id": "test-conv"},
            )

        # Pydantic validation error for min_length returns 422
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_chat_whitespace_message_returns_400(self, llm_service_with_mock):
        """Test that whitespace-only message returns 400 error."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "   ", "conversation_id": "test-conv"},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.EMPTY_MESSAGE

    async def test_chat_message_too_long_returns_422(self, llm_service_with_mock):
        """Test that message exceeding limit returns 422 validation error."""
        long_message = "あ" * 4001

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": long_message, "conversation_id": "test-conv"},
            )

        # Pydantic validation error for max_length returns 422
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    async def test_chat_invalid_conversation_id_returns_400(
        self, llm_service_with_mock
    ):
        """Test that invalid conversation ID format returns 400 error."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "Hello", "conversation_id": "invalid id!@#"},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.INVALID_CONVERSATION_ID

    async def test_chat_no_api_key_returns_503(self, llm_service_unconfigured):
        """Test that missing API key returns 503 error."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "Hello", "conversation_id": "test-conv"},
            )

        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.LLM_NOT_CONFIGURED


class TestChatErrorResponses:
    """Tests for error responses (T014)."""

    async def test_rate_limit_returns_503(self, llm_service_with_mock):
        """Test that rate limit error returns 503."""
        from openai import RateLimitError

        llm_service_with_mock._client.chat.completions.create.side_effect = (
            RateLimitError(
                message="Rate limit exceeded",
                response=MagicMock(status_code=429),
                body=None,
            )
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "Hello", "conversation_id": "test-conv"},
            )

        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.LLM_RATE_LIMITED

    async def test_connection_error_returns_503(self, llm_service_with_mock):
        """Test that connection error returns 503."""
        from openai import APIConnectionError

        llm_service_with_mock._client.chat.completions.create.side_effect = (
            APIConnectionError(request=MagicMock())
        )

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/llm/chat",
                json={"message": "Hello", "conversation_id": "test-conv"},
            )

        assert response.status_code == 503
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.LLM_CONNECTION_ERROR


# =============================================================================
# User Story 2: 会話コンテキストの維持 (T028-T029)
# =============================================================================


class TestConversationContext:
    """Tests for conversation context (T028)."""

    async def test_multi_turn_conversation(self, llm_service_with_mock):
        """Test that conversation context is maintained across requests."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # First message
            response1 = await client.post(
                "/api/llm/chat",
                json={"message": "私の名前は田中です", "conversation_id": "multi-turn"},
            )
            assert response1.status_code == 200

            # Second message - context should include first message
            response2 = await client.post(
                "/api/llm/chat",
                json={
                    "message": "私の名前は何ですか？",
                    "conversation_id": "multi-turn",
                },
            )
            assert response2.status_code == 200

        # Verify the service received both messages
        conv = llm_service_with_mock._conversation_cache.get_or_create("multi-turn")
        # Should have 2 user messages and 2 assistant messages
        assert len(conv.messages) == 4


class TestClearConversation:
    """Tests for DELETE /api/llm/conversations/{id} (T029)."""

    async def test_clear_existing_conversation(self, llm_service_with_mock):
        """Test clearing an existing conversation."""
        # Add a message first
        llm_service_with_mock._conversation_cache.add_message(
            "to-clear", "user", "Hello"
        )
        assert llm_service_with_mock._conversation_cache.count() == 1

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.delete("/api/llm/conversations/to-clear")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Conversation cleared"
        assert data["conversation_id"] == "to-clear"
        assert llm_service_with_mock._conversation_cache.count() == 0

    async def test_clear_nonexistent_conversation(self, llm_service_with_mock):
        """Test clearing a conversation that doesn't exist returns success."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.delete("/api/llm/conversations/nonexistent")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Conversation cleared"

    async def test_clear_invalid_conversation_id_returns_400(
        self, llm_service_with_mock
    ):
        """Test that invalid conversation ID returns 400."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.delete("/api/llm/conversations/invalid@id!")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error_code"] == ErrorCode.INVALID_CONVERSATION_ID


# =============================================================================
# User Story 3: サービス健全性の確認 (T038-T039)
# =============================================================================


class TestStatusEndpoint:
    """Tests for GET /api/llm/status (T038-T039)."""

    async def test_status_healthy(self, llm_service_with_mock):
        """Test status endpoint returns healthy when configured."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/llm/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["api_configured"] is True
        assert data["model"] == "gpt-4o-mini"

    async def test_status_unhealthy_no_api_key(self, llm_service_unconfigured):
        """Test status endpoint returns unhealthy when not configured."""
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/llm/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["api_configured"] is False
        assert "OPENAI_API_KEY" in data["error_message"]

    async def test_status_includes_conversation_count(self, llm_service_with_mock):
        """Test that status includes active conversation count."""
        llm_service_with_mock._conversation_cache.add_message("conv1", "user", "hi")
        llm_service_with_mock._conversation_cache.add_message("conv2", "user", "hello")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/llm/status")

        assert response.status_code == 200
        data = response.json()
        assert data["active_conversations"] == 2
