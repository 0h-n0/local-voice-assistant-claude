"""Contract tests for Conversation History API endpoints.

Tests verify API responses match the OpenAPI specification.
"""

import asyncio
import uuid
from collections.abc import Coroutine
from typing import Any, TypeVar

import pytest
from fastapi.testclient import TestClient

from src.db.database import DatabaseManager
from src.dependencies import (
    set_conversation_storage_service,
    set_db_manager,
)
from src.main import app
from src.models.conversation import MessageRole
from src.services.conversation_storage_service import ConversationStorageService

T = TypeVar("T")


def _run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run an async coroutine in a new event loop.

    This avoids the deprecated asyncio.get_event_loop() warning in Python 3.10+.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = str(tmp_path / "test_conversations.db")
    manager = DatabaseManager(db_path)
    _run_async(manager.initialize())
    set_db_manager(manager)
    yield manager
    _run_async(manager.close())


@pytest.fixture
def storage_service(test_db):
    """Create a storage service with test database."""
    service = ConversationStorageService(test_db)
    set_conversation_storage_service(service)
    return service


@pytest.fixture
def client(storage_service):
    """Create test client with initialized services."""
    return TestClient(app, raise_server_exceptions=False)


class TestListConversationsContract:
    """Contract tests for GET /api/conversations."""

    def test_response_has_required_fields(self, client):
        """Test response contains required fields per OpenAPI spec."""
        response = client.get("/api/conversations")
        assert response.status_code == 200

        data = response.json()
        assert "conversations" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    def test_response_types(self, client):
        """Test response field types match OpenAPI spec."""
        response = client.get("/api/conversations")
        data = response.json()

        assert isinstance(data["conversations"], list)
        assert isinstance(data["total"], int)
        assert isinstance(data["limit"], int)
        assert isinstance(data["offset"], int)

    def test_pagination_defaults(self, client):
        """Test default pagination values."""
        response = client.get("/api/conversations")
        data = response.json()

        assert data["limit"] == 20
        assert data["offset"] == 0

    def test_pagination_parameters(self, client):
        """Test custom pagination parameters."""
        response = client.get("/api/conversations?limit=10&offset=5")
        data = response.json()

        assert data["limit"] == 10
        assert data["offset"] == 5


class TestGetConversationContract:
    """Contract tests for GET /api/conversations/{id}."""

    @pytest.fixture
    def sample_conversation(self, storage_service):
        """Create a sample conversation for testing."""
        conversation_id = str(uuid.uuid4())
        _run_async(
            storage_service.save_message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Hello",
            )
        )
        _run_async(
            storage_service.save_message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                content="Hi there!",
            )
        )
        return conversation_id

    def test_response_has_required_fields(self, client, sample_conversation):
        """Test response contains required fields per OpenAPI spec."""
        response = client.get(f"/api/conversations/{sample_conversation}")
        assert response.status_code == 200

        data = response.json()
        assert "id" in data
        assert "messages" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_message_has_required_fields(self, client, sample_conversation):
        """Test each message contains required fields per OpenAPI spec."""
        response = client.get(f"/api/conversations/{sample_conversation}")
        data = response.json()

        for message in data["messages"]:
            assert "id" in message
            assert "role" in message
            assert "content" in message
            assert "created_at" in message

    def test_message_role_values(self, client, sample_conversation):
        """Test message roles are valid enum values."""
        response = client.get(f"/api/conversations/{sample_conversation}")
        data = response.json()

        for message in data["messages"]:
            assert message["role"] in ["user", "assistant"]

    def test_not_found_error_format(self, client):
        """Test 404 error response format matches OpenAPI spec."""
        nonexistent_uuid = str(uuid.uuid4())
        response = client.get(f"/api/conversations/{nonexistent_uuid}")
        assert response.status_code == 404

        data = response.json()
        # FastAPI wraps the error in a 'detail' key
        detail = data.get("detail", data)
        assert "error_code" in detail
        assert "message" in detail
        assert detail["error_code"] == "CONVERSATION_NOT_FOUND"


class TestDeleteConversationContract:
    """Contract tests for DELETE /api/conversations/{id}."""

    @pytest.fixture
    def deletable_conversation(self, storage_service):
        """Create a conversation that can be deleted."""
        conversation_id = str(uuid.uuid4())
        _run_async(
            storage_service.save_message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="To be deleted",
            )
        )
        return conversation_id

    def test_successful_delete_returns_204(self, client, deletable_conversation):
        """Test successful delete returns 204 No Content."""
        response = client.delete(f"/api/conversations/{deletable_conversation}")
        assert response.status_code == 204
        assert response.content == b""

    def test_not_found_error_format(self, client):
        """Test 404 error response format matches OpenAPI spec."""
        nonexistent_uuid = str(uuid.uuid4())
        response = client.delete(f"/api/conversations/{nonexistent_uuid}")
        assert response.status_code == 404

        data = response.json()
        # FastAPI wraps the error in a 'detail' key
        detail = data.get("detail", data)
        assert "error_code" in detail
        assert "message" in detail
        assert detail["error_code"] == "CONVERSATION_NOT_FOUND"
