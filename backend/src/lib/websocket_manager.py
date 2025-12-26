"""WebSocket Connection Manager.

Manages WebSocket connections, session tracking, and message broadcasting.
"""

import asyncio
import contextlib
import logging
import uuid

from fastapi import WebSocket

from src.models.websocket import (
    ConnectionAckMessage,
    ErrorMessage,
    PingMessage,
    ProcessingStatus,
    ServerMessage,
    StatusUpdateMessage,
    WebSocketErrorCode,
)

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and session lifecycle."""

    def __init__(self) -> None:
        """Initialize the connection manager."""
        # Active connections: session_id -> websocket
        self._connections: dict[str, WebSocket] = {}
        # Ping task handles for cleanup
        self._ping_tasks: dict[str, asyncio.Task[None]] = {}

    @property
    def active_connections(self) -> int:
        """Return number of active connections."""
        return len(self._connections)

    def get_session_ids(self) -> list[str]:
        """Return list of active session IDs."""
        return list(self._connections.keys())

    async def connect(self, websocket: WebSocket) -> str:
        """Accept a WebSocket connection and assign a session ID.

        Args:
            websocket: The WebSocket connection to accept.

        Returns:
            The assigned session ID.
        """
        await websocket.accept()
        session_id = str(uuid.uuid4())
        self._connections[session_id] = websocket

        # Send connection acknowledgement (server_time uses default_factory)
        ack = ConnectionAckMessage(session_id=session_id)
        await self.send_message(session_id, ack)

        return session_id

    async def disconnect(self, session_id: str) -> None:
        """Disconnect a WebSocket session.

        Args:
            session_id: The session ID to disconnect.
        """
        # Cancel ping task if running
        if session_id in self._ping_tasks:
            self._ping_tasks[session_id].cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._ping_tasks[session_id]
            del self._ping_tasks[session_id]

        # Remove connection
        if session_id in self._connections:
            del self._connections[session_id]

    def get_websocket(self, session_id: str) -> WebSocket | None:
        """Get the WebSocket for a session.

        Args:
            session_id: The session ID.

        Returns:
            The WebSocket or None if not found.
        """
        return self._connections.get(session_id)

    async def send_message(self, session_id: str, message: ServerMessage) -> bool:
        """Send a message to a specific session.

        Args:
            session_id: The session ID to send to.
            message: The message to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        websocket = self._connections.get(session_id)
        if websocket is None:
            return False

        try:
            await websocket.send_json(message.model_dump(mode="json"))
            return True
        except Exception:
            logger.warning(
                "Failed to send message to session %s, disconnecting", session_id
            )
            await self.disconnect(session_id)
            return False

    async def send_status_update(
        self, session_id: str, status: ProcessingStatus
    ) -> bool:
        """Send a status update to a session.

        Args:
            session_id: The session ID.
            status: The new processing status.

        Returns:
            True if sent successfully.
        """
        message = StatusUpdateMessage(status=status)
        return await self.send_message(session_id, message)

    async def send_error(
        self,
        session_id: str,
        code: WebSocketErrorCode,
        message: str,
        *,
        recoverable: bool = False,
        details: dict[str, object] | None = None,
    ) -> bool:
        """Send an error message to a session.

        Args:
            session_id: The session ID.
            code: The error code.
            message: Human-readable error message.
            recoverable: Whether the client can retry.
            details: Optional additional error details.

        Returns:
            True if sent successfully.
        """
        error = ErrorMessage(
            code=code,
            message=message,
            recoverable=recoverable,
            details=details,
        )
        return await self.send_message(session_id, error)

    async def broadcast(self, message: ServerMessage) -> int:
        """Broadcast a message to all connected sessions.

        Args:
            message: The message to broadcast.

        Returns:
            Number of sessions the message was sent to.
        """
        sent_count = 0
        # Copy keys to avoid modification during iteration
        for session_id in list(self._connections.keys()):
            if await self.send_message(session_id, message):
                sent_count += 1
        return sent_count

    async def start_ping_loop(
        self, session_id: str, interval_seconds: int = 30
    ) -> None:
        """Start a ping loop for a session.

        Args:
            session_id: The session ID.
            interval_seconds: Interval between pings.
        """
        if session_id in self._ping_tasks:
            return  # Already running

        async def ping_loop() -> None:
            try:
                while session_id in self._connections:
                    await asyncio.sleep(interval_seconds)
                    if session_id in self._connections:
                        ping = PingMessage()
                        await self.send_message(session_id, ping)
            except asyncio.CancelledError:
                pass

        self._ping_tasks[session_id] = asyncio.create_task(ping_loop())


# Global connection manager instance
connection_manager = ConnectionManager()
