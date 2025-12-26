"""Integration tests for Conversation History API endpoints."""

import time

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


@pytest.fixture
def test_db(tmp_path):
    """Create a temporary database for testing."""
    import asyncio

    db_path = str(tmp_path / "test_conversations.db")
    manager = DatabaseManager(db_path)
    asyncio.get_event_loop().run_until_complete(manager.initialize())
    set_db_manager(manager)
    yield manager
    asyncio.get_event_loop().run_until_complete(manager.close())


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


class TestListConversations:
    """Integration tests for GET /api/conversations."""

    def test_list_empty_returns_empty_list(self, client):
        """Test listing conversations when none exist."""
        response = client.get("/api/conversations")
        assert response.status_code == 200

        data = response.json()
        assert data["conversations"] == []
        assert data["total"] == 0

    def test_list_returns_conversations_in_order(self, client, storage_service):
        """Test conversations are returned in most recent order."""
        import asyncio
        import time

        # Create conversations with slight delay
        for i in range(3):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=f"conv-{i}",
                    role=MessageRole.USER,
                    content=f"Message {i}",
                )
            )
            time.sleep(0.01)  # Small delay to ensure different timestamps

        response = client.get("/api/conversations")
        data = response.json()

        assert len(data["conversations"]) == 3
        # Most recent should be first
        assert data["conversations"][0]["id"] == "conv-2"
        assert data["conversations"][2]["id"] == "conv-0"

    def test_list_pagination_works(self, client, storage_service):
        """Test pagination returns correct subset."""
        import asyncio

        # Create 5 conversations
        for i in range(5):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=f"page-conv-{i}",
                    role=MessageRole.USER,
                    content=f"Message {i}",
                )
            )

        # Get first page of 2
        response = client.get("/api/conversations?limit=2&offset=0")
        data = response.json()

        assert len(data["conversations"]) == 2
        assert data["total"] == 5
        assert data["limit"] == 2
        assert data["offset"] == 0

    def test_list_shows_message_count(self, client, storage_service):
        """Test message_count reflects actual messages."""
        import asyncio

        conv_id = "count-test"
        for i in range(3):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=conv_id,
                    role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                    content=f"Message {i}",
                )
            )

        response = client.get("/api/conversations")
        data = response.json()

        conv = next(c for c in data["conversations"] if c["id"] == conv_id)
        assert conv["message_count"] == 3


class TestGetConversationDetail:
    """Integration tests for GET /api/conversations/{id}."""

    def test_get_returns_all_messages(self, client, storage_service):
        """Test getting conversation returns all messages."""
        import asyncio

        conv_id = "detail-test"
        asyncio.get_event_loop().run_until_complete(
            storage_service.save_message(
                conversation_id=conv_id,
                role=MessageRole.USER,
                content="Hello",
            )
        )
        asyncio.get_event_loop().run_until_complete(
            storage_service.save_message(
                conversation_id=conv_id,
                role=MessageRole.ASSISTANT,
                content="Hi there!",
            )
        )

        response = client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == conv_id
        assert len(data["messages"]) == 2
        assert data["messages"][0]["content"] == "Hello"
        assert data["messages"][1]["content"] == "Hi there!"

    def test_messages_in_chronological_order(self, client, storage_service):
        """Test messages are returned in chronological order."""
        import asyncio

        conv_id = "order-test"
        messages = ["First", "Second", "Third"]
        for msg in messages:
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=conv_id,
                    role=MessageRole.USER,
                    content=msg,
                )
            )

        response = client.get(f"/api/conversations/{conv_id}")
        data = response.json()

        for i, msg in enumerate(messages):
            assert data["messages"][i]["content"] == msg

    def test_get_nonexistent_returns_404(self, client):
        """Test getting nonexistent conversation returns 404."""
        response = client.get("/api/conversations/does-not-exist")
        assert response.status_code == 404


class TestDeleteConversation:
    """Integration tests for DELETE /api/conversations/{id}."""

    def test_delete_removes_conversation(self, client, storage_service):
        """Test delete removes conversation from list."""
        import asyncio

        conv_id = "to-delete"
        asyncio.get_event_loop().run_until_complete(
            storage_service.save_message(
                conversation_id=conv_id,
                role=MessageRole.USER,
                content="Delete me",
            )
        )

        # Verify it exists
        response = client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 200

        # Delete it
        response = client.delete(f"/api/conversations/{conv_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/api/conversations/{conv_id}")
        assert response.status_code == 404

    def test_delete_cascade_removes_messages(self, client, storage_service, test_db):
        """Test delete cascades to remove all messages."""
        import asyncio

        conv_id = "cascade-test"
        for i in range(3):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=conv_id,
                    role=MessageRole.USER,
                    content=f"Message {i}",
                )
            )

        # Delete conversation
        response = client.delete(f"/api/conversations/{conv_id}")
        assert response.status_code == 204

        # Verify messages are also deleted
        cursor = asyncio.get_event_loop().run_until_complete(
            test_db.connection.execute(
                "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
                (conv_id,),
            )
        )
        row = asyncio.get_event_loop().run_until_complete(cursor.fetchone())
        assert row[0] == 0

    def test_delete_nonexistent_returns_404(self, client):
        """Test deleting nonexistent conversation returns 404."""
        response = client.delete("/api/conversations/does-not-exist")
        assert response.status_code == 404


class TestPerformance:
    """Performance validation tests."""

    def test_save_performance_under_100ms(self, storage_service):
        """Test save_message completes in under 100ms."""
        import asyncio

        conversation_id = "perf-save-test"

        start = time.perf_counter()
        asyncio.get_event_loop().run_until_complete(
            storage_service.save_message(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                content="Performance test message",
            )
        )
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert elapsed < 100, f"Save took {elapsed:.2f}ms, expected < 100ms"

    def test_retrieval_100_messages_under_500ms(self, storage_service, client):
        """Test retrieving 100 messages completes in under 500ms."""
        import asyncio

        conversation_id = "perf-retrieve-test"

        # Create 100 messages
        for i in range(100):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=conversation_id,
                    role=MessageRole.USER if i % 2 == 0 else MessageRole.ASSISTANT,
                    content=f"Message {i}" * 10,  # ~100 chars each
                )
            )

        start = time.perf_counter()
        response = client.get(f"/api/conversations/{conversation_id}")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert response.status_code == 200
        assert len(response.json()["messages"]) == 100
        assert elapsed < 500, f"Retrieval took {elapsed:.2f}ms, expected < 500ms"

    def test_list_20_conversations_under_200ms(self, storage_service, client):
        """Test listing 20 conversations completes in under 200ms."""
        import asyncio

        # Create 25 conversations
        for i in range(25):
            asyncio.get_event_loop().run_until_complete(
                storage_service.save_message(
                    conversation_id=f"perf-list-conv-{i}",
                    role=MessageRole.USER,
                    content=f"Message in conversation {i}",
                )
            )

        start = time.perf_counter()
        response = client.get("/api/conversations?limit=20")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert response.status_code == 200
        assert len(response.json()["conversations"]) == 20
        assert elapsed < 200, f"List took {elapsed:.2f}ms, expected < 200ms"
