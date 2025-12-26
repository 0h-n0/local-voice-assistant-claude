"""SQLite database connection management with async support."""

import logging
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)

# SQL schema for conversation storage
SCHEMA = """
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at DESC);
"""


class DatabaseManager:
    """Manages SQLite database connections with async support."""

    def __init__(self, db_path: str) -> None:
        """Initialize database manager.

        Args:
            db_path: Path to SQLite database file.
        """
        self._db_path = db_path
        self._connection: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Initialize database connection and schema.

        Creates database file and tables if they don't exist.
        Enables WAL mode and foreign key constraints.
        """
        db_dir = Path(self._db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self._connection = await aiosqlite.connect(self._db_path)

        await self._connection.execute("PRAGMA journal_mode=WAL")
        await self._connection.execute("PRAGMA foreign_keys=ON")

        await self._connection.executescript(SCHEMA)
        await self._connection.commit()

        logger.info("Database initialized at %s", self._db_path)

    async def close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("Database connection closed")

    @property
    def connection(self) -> aiosqlite.Connection:
        """Get the active database connection.

        Returns:
            Active database connection.

        Raises:
            RuntimeError: If database is not initialized.
        """
        if self._connection is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self._connection
