"""Conversation storage service for persisting dialogue history."""

import logging
from datetime import UTC, datetime

from src.db.database import DatabaseManager
from src.models.conversation import (
    ConversationDetail,
    ConversationListResponse,
    ConversationSummary,
    MessageResponse,
    MessageRole,
)

logger = logging.getLogger(__name__)


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found."""

    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id
        super().__init__(f"Conversation with ID {conversation_id} not found")


class ConversationStorageService:
    """Service for storing and retrieving conversation history."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize the service with a database manager.

        Args:
            db_manager: Database manager instance.
        """
        self._db = db_manager

    async def save_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
    ) -> int:
        """Save a message to the conversation history.

        Creates a new conversation record if this is the first message
        for the given conversation_id.

        Args:
            conversation_id: Unique identifier for the conversation.
            role: Message sender role (user or assistant).
            content: Message text content.

        Returns:
            The ID of the saved message.
        """
        conn = self._db.connection
        now = datetime.now(UTC).isoformat()

        existing = await conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        row = await existing.fetchone()

        if row is None:
            await conn.execute(
                """INSERT INTO conversations (id, created_at, updated_at)
                VALUES (?, ?, ?)""",
                (conversation_id, now, now),
            )
            logger.info("Created new conversation: %s", conversation_id)
        else:
            await conn.execute(
                "UPDATE conversations SET updated_at = ? WHERE id = ?",
                (now, conversation_id),
            )

        cursor = await conn.execute(
            """INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (?, ?, ?, ?)""",
            (conversation_id, role.value, content, now),
        )
        await conn.commit()

        message_id = cursor.lastrowid
        logger.info(
            "Saved message %d for conversation %s (role=%s, length=%d)",
            message_id,
            conversation_id,
            role.value,
            len(content),
        )
        return message_id  # type: ignore[return-value]

    async def list_conversations(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> ConversationListResponse:
        """List conversations with pagination.

        Args:
            limit: Maximum number of conversations to return.
            offset: Number of conversations to skip.

        Returns:
            Paginated list of conversation summaries.
        """
        conn = self._db.connection

        # Get total count
        cursor = await conn.execute("SELECT COUNT(*) FROM conversations")
        row = await cursor.fetchone()
        total: int = row[0] if row else 0

        # Get conversations with message counts
        cursor = await conn.execute(
            """
            SELECT c.id, c.created_at, c.updated_at, COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id
            ORDER BY c.updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )
        rows = await cursor.fetchall()

        conversations = [
            ConversationSummary(
                id=row[0],
                created_at=datetime.fromisoformat(row[1]),
                updated_at=datetime.fromisoformat(row[2]),
                message_count=row[3],
            )
            for row in rows
        ]

        logger.info(
            "Listed %d conversations (total=%d, limit=%d, offset=%d)",
            len(conversations),
            total,
            limit,
            offset,
        )

        return ConversationListResponse(
            conversations=conversations,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_conversation(
        self,
        conversation_id: str,
    ) -> ConversationDetail:
        """Get a conversation with all its messages.

        Args:
            conversation_id: Unique identifier for the conversation.

        Returns:
            Conversation detail with all messages.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
        """
        conn = self._db.connection

        # Get conversation
        cursor = await conn.execute(
            "SELECT id, created_at, updated_at FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        conv_row = await cursor.fetchone()

        if conv_row is None:
            raise ConversationNotFoundError(conversation_id)

        # Get messages
        cursor = await conn.execute(
            """
            SELECT id, role, content, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            """,
            (conversation_id,),
        )
        message_rows = await cursor.fetchall()

        messages = [
            MessageResponse(
                id=row[0],
                role=MessageRole(row[1]),
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
            )
            for row in message_rows
        ]

        logger.info(
            "Retrieved conversation %s with %d messages",
            conversation_id,
            len(messages),
        )

        return ConversationDetail(
            id=conv_row[0],
            messages=messages,
            created_at=datetime.fromisoformat(conv_row[1]),
            updated_at=datetime.fromisoformat(conv_row[2]),
        )

    async def delete_conversation(
        self,
        conversation_id: str,
    ) -> None:
        """Delete a conversation and all its messages.

        Args:
            conversation_id: Unique identifier for the conversation.

        Raises:
            ConversationNotFoundError: If conversation doesn't exist.
        """
        conn = self._db.connection

        # Check if conversation exists
        cursor = await conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        if await cursor.fetchone() is None:
            raise ConversationNotFoundError(conversation_id)

        # Delete conversation (messages are deleted via CASCADE)
        await conn.execute(
            "DELETE FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        await conn.commit()

        logger.info("Deleted conversation %s", conversation_id)
