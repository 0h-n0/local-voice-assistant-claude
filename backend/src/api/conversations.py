"""REST API endpoints for conversation history."""

import logging
import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from src.dependencies import get_conversation_storage_service
from src.models.conversation import (
    ConversationDetail,
    ConversationErrorCode,
    ConversationErrorResponse,
    ConversationListResponse,
)
from src.services.conversation_storage_service import (
    ConversationNotFoundError,
    ConversationStorageService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

# UUID validation pattern
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


def _validate_uuid(conversation_id: str) -> None:
    """Validate that conversation_id is a valid UUID format."""
    if not re.match(UUID_PATTERN, conversation_id, re.IGNORECASE):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.CONVERSATION_NOT_FOUND,
                message=f"Invalid conversation ID format: {conversation_id}",
            ).model_dump(),
        )


@router.get(
    "",
    response_model=ConversationListResponse,
    responses={
        503: {"model": ConversationErrorResponse, "description": "Database error"},
    },
)
async def list_conversations(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    storage: ConversationStorageService = Depends(  # noqa: B008
        get_conversation_storage_service
    ),
) -> ConversationListResponse:
    """List conversations with pagination.

    Returns a paginated list of conversation summaries, ordered by most recent.
    """
    try:
        return await storage.list_conversations(limit=limit, offset=offset)
    except Exception as e:
        logger.exception("Database error listing conversations")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.DATABASE_ERROR,
                message=f"Failed to list conversations: {e}",
            ).model_dump(),
        ) from e


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetail,
    responses={
        404: {
            "model": ConversationErrorResponse,
            "description": "Conversation not found",
        },
        503: {"model": ConversationErrorResponse, "description": "Database error"},
    },
)
async def get_conversation(
    conversation_id: Annotated[str, Path(description="Conversation ID (UUID format)")],
    storage: ConversationStorageService = Depends(  # noqa: B008
        get_conversation_storage_service
    ),
) -> ConversationDetail:
    """Get a conversation with all its messages.

    Returns the full conversation detail including all messages in chronological order.
    """
    _validate_uuid(conversation_id)
    try:
        return await storage.get_conversation(conversation_id)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.CONVERSATION_NOT_FOUND,
                message=f"Conversation with ID {conversation_id} not found",
            ).model_dump(),
        ) from None
    except Exception as e:
        logger.exception("Database error getting conversation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.DATABASE_ERROR,
                message=f"Failed to get conversation: {e}",
            ).model_dump(),
        ) from e


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ConversationErrorResponse,
            "description": "Conversation not found",
        },
        503: {"model": ConversationErrorResponse, "description": "Database error"},
    },
)
async def delete_conversation(
    conversation_id: Annotated[str, Path(description="Conversation ID (UUID format)")],
    storage: ConversationStorageService = Depends(  # noqa: B008
        get_conversation_storage_service
    ),
) -> Response:
    """Delete a conversation and all its messages.

    Returns 204 No Content on success.
    """
    _validate_uuid(conversation_id)
    try:
        await storage.delete_conversation(conversation_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ConversationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.CONVERSATION_NOT_FOUND,
                message=f"Conversation with ID {conversation_id} not found",
            ).model_dump(),
        ) from None
    except Exception as e:
        logger.exception("Database error deleting conversation")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ConversationErrorResponse(
                error_code=ConversationErrorCode.DATABASE_ERROR,
                message=f"Failed to delete conversation: {e}",
            ).model_dump(),
        ) from e
