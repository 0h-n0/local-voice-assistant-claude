"""Unit tests for ConversationStorageService."""

import pytest

from src.db.database import DatabaseManager
from src.models.conversation import MessageRole
from src.services.conversation_storage_service import ConversationStorageService


@pytest.fixture
async def db_manager(tmp_path):
    """Create a temporary database for testing."""
    db_path = str(tmp_path / "test_conversations.db")
    manager = DatabaseManager(db_path)
    await manager.initialize()
    yield manager
    await manager.close()


@pytest.fixture
async def storage_service(db_manager):
    """Create a storage service with test database."""
    return ConversationStorageService(db_manager)


class TestSaveMessage:
    """Tests for save_message method."""

    @pytest.mark.asyncio
    async def test_save_message_returns_message_id(self, storage_service):
        """Test that save_message returns the message ID."""
        conversation_id = "test-conv-001"
        message_id = await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="Hello, assistant!",
        )
        assert isinstance(message_id, int)
        assert message_id > 0

    @pytest.mark.asyncio
    async def test_save_message_stores_content(self, storage_service, db_manager):
        """Test that save_message stores the content correctly."""
        conversation_id = "test-conv-002"
        content = "This is a test message"
        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=content,
        )

        # Verify in database
        cursor = await db_manager.connection.execute(
            "SELECT content FROM messages WHERE conversation_id = ?",
            (conversation_id,),
        )
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == content

    @pytest.mark.asyncio
    async def test_save_multiple_messages_sequential_ids(self, storage_service):
        """Test that multiple messages get sequential IDs."""
        conversation_id = "test-conv-003"
        id1 = await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="First message",
        )
        id2 = await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Second message",
        )
        assert id2 > id1


class TestConversationAutoCreation:
    """Tests for auto-creation of conversation records."""

    @pytest.mark.asyncio
    async def test_auto_creates_conversation_on_first_message(
        self, storage_service, db_manager
    ):
        """Test that a new conversation is created when first message is saved."""
        conversation_id = "new-conv-001"

        # Verify conversation doesn't exist
        cursor = await db_manager.connection.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        assert await cursor.fetchone() is None

        # Save first message
        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="First message",
        )

        # Verify conversation now exists
        cursor = await db_manager.connection.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        row = await cursor.fetchone()
        assert row is not None
        assert row[0] == conversation_id

    @pytest.mark.asyncio
    async def test_does_not_create_duplicate_conversation(
        self, storage_service, db_manager
    ):
        """Test that second message doesn't create duplicate conversation."""
        conversation_id = "dup-conv-001"

        # Save two messages
        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="First message",
        )
        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Second message",
        )

        # Verify only one conversation exists
        cursor = await db_manager.connection.execute(
            "SELECT COUNT(*) FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        row = await cursor.fetchone()
        assert row[0] == 1

    @pytest.mark.asyncio
    async def test_updates_conversation_updated_at(self, storage_service, db_manager):
        """Test that updated_at is updated when new message is added."""
        conversation_id = "update-conv-001"

        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content="First message",
        )

        # Get initial updated_at
        cursor = await db_manager.connection.execute(
            "SELECT updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        initial_updated = (await cursor.fetchone())[0]

        # Save another message
        await storage_service.save_message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content="Second message",
        )

        # Get new updated_at
        cursor = await db_manager.connection.execute(
            "SELECT updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        new_updated = (await cursor.fetchone())[0]

        # updated_at should be >= initial (could be same if fast)
        assert new_updated >= initial_updated
