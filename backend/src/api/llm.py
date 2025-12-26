"""LLM API endpoints for text response generation."""

import logging
import re
import time

from fastapi import APIRouter, HTTPException, Path, status

from src.dependencies import get_llm_service
from src.models.llm import (
    ErrorCode,
    ErrorResponse,
    LLMRequest,
    LLMResponse,
    LLMStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/llm", tags=["llm"])

# Conversation ID validation pattern
CONVERSATION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_conversation_id(conversation_id: str) -> None:
    """Validate conversation ID format.

    Args:
        conversation_id: ID to validate

    Raises:
        HTTPException: If ID format is invalid
    """
    if not conversation_id or len(conversation_id) > 64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error_code=ErrorCode.INVALID_CONVERSATION_ID,
                message="Conversation ID must be 1-64 characters",
            ).model_dump(),
        )
    if not CONVERSATION_ID_PATTERN.match(conversation_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error_code=ErrorCode.INVALID_CONVERSATION_ID,
                message="Conversation ID must be alphanumeric with hyphens/underscores",
            ).model_dump(),
        )


@router.post(
    "/chat",
    response_model=LLMResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Processing error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"},
    },
)
async def chat(request: LLMRequest) -> LLMResponse:
    """Generate LLM response for a text message.

    Maintains conversation context via conversation_id.
    """
    logger.info(
        "Chat request received: conversation_id=%s, message_length=%d",
        request.conversation_id,
        len(request.message),
    )
    request_start = time.time()

    # Validate conversation ID format
    _validate_conversation_id(request.conversation_id)

    try:
        llm_service = get_llm_service()
    except RuntimeError as e:
        logger.error("LLM service not initialized: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=ErrorResponse(
                error_code=ErrorCode.LLM_NOT_CONFIGURED,
                message="LLM service not initialized",
            ).model_dump(),
        ) from e

    try:
        text, usage = await llm_service.generate_response(
            request.message, request.conversation_id
        )
        processing_time = time.time() - request_start

        logger.info(
            "Chat response generated: conversation_id=%s, "
            "response_length=%d, processing_time=%.2fs",
            request.conversation_id,
            len(text),
            processing_time,
        )

        return LLMResponse(
            text=text,
            conversation_id=request.conversation_id,
            usage=usage,
            processing_time_seconds=processing_time,
        )

    except ValueError as e:
        error_str = str(e)
        if ErrorCode.EMPTY_MESSAGE in error_str:
            logger.warning("Chat request rejected: empty message")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.EMPTY_MESSAGE,
                    message="Message content is empty or whitespace",
                ).model_dump(),
            ) from e
        if ErrorCode.MESSAGE_TOO_LONG in error_str:
            logger.warning("Chat request rejected: message too long")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(
                    error_code=ErrorCode.MESSAGE_TOO_LONG,
                    message="Message exceeds 4000 character limit",
                    details={"max_length": 4000},
                ).model_dump(),
            ) from e
        logger.error("Validation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorResponse(
                error_code=ErrorCode.LLM_PROCESSING_ERROR,
                message=str(e),
            ).model_dump(),
        ) from e

    except RuntimeError as e:
        error_str = str(e)
        if ErrorCode.LLM_NOT_CONFIGURED in error_str:
            logger.error("LLM not configured")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error_code=ErrorCode.LLM_NOT_CONFIGURED,
                    message="OpenAI API key is not configured",
                ).model_dump(),
            ) from e
        if ErrorCode.LLM_RATE_LIMITED in error_str:
            logger.warning("LLM rate limited")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error_code=ErrorCode.LLM_RATE_LIMITED,
                    message="Rate limited by OpenAI API, please try again later",
                ).model_dump(),
            ) from e
        if ErrorCode.LLM_CONNECTION_ERROR in error_str:
            logger.error("LLM connection error")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=ErrorResponse(
                    error_code=ErrorCode.LLM_CONNECTION_ERROR,
                    message="Cannot connect to OpenAI API",
                ).model_dump(),
            ) from e
        if ErrorCode.LLM_API_ERROR in error_str:
            logger.error("LLM API error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ErrorResponse(
                    error_code=ErrorCode.LLM_API_ERROR,
                    message="OpenAI API returned an error",
                ).model_dump(),
            ) from e
        logger.exception("LLM processing error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error_code=ErrorCode.LLM_PROCESSING_ERROR,
                message="Failed to generate response",
            ).model_dump(),
        ) from e

    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error_code=ErrorCode.LLM_PROCESSING_ERROR,
                message="An unexpected error occurred",
            ).model_dump(),
        ) from e


@router.delete(
    "/conversations/{conversation_id}",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid conversation ID"},
    },
)
async def clear_conversation(
    conversation_id: str = Path(..., min_length=1, max_length=64),
) -> dict[str, str]:
    """Clear the conversation history for a specific conversation ID.

    Returns success even if the conversation doesn't exist.
    """
    logger.info("Clear conversation request: conversation_id=%s", conversation_id)

    _validate_conversation_id(conversation_id)

    try:
        llm_service = get_llm_service()
        cleared = llm_service.clear_conversation(conversation_id)
        if cleared:
            logger.info("Conversation cleared: %s", conversation_id)
        else:
            logger.debug(
                "Conversation not found (already cleared): %s", conversation_id
            )
    except RuntimeError:
        # Service not initialized - conversation doesn't exist anyway
        logger.debug("LLM service not initialized, conversation does not exist")

    return {"message": "Conversation cleared", "conversation_id": conversation_id}


@router.get(
    "/status",
    response_model=LLMStatus,
)
async def get_status() -> LLMStatus:
    """Get the current status of the LLM service.

    Returns configuration state and active conversation count.
    """
    logger.debug("Status request received")

    try:
        llm_service = get_llm_service()
        llm_status = llm_service.get_status()
        logger.debug(
            "Status: status=%s, model=%s, api_configured=%s, conversations=%d",
            llm_status.status,
            llm_status.model,
            llm_status.api_configured,
            llm_status.active_conversations,
        )
        return llm_status
    except RuntimeError:
        # Service not initialized
        from src.services.llm_service import DEFAULT_MODEL

        logger.warning("LLM service not initialized")
        return LLMStatus(
            status="unhealthy",  # type: ignore[arg-type]
            model=DEFAULT_MODEL,
            api_configured=False,
            active_conversations=0,
            error_message="LLM service not initialized",
        )
