"""Dependency injection for FastAPI."""

from src.db.database import DatabaseManager
from src.services.conversation_storage_service import ConversationStorageService
from src.services.llm_service import LLMService
from src.services.orchestrator_service import OrchestratorService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService

# Global service instances
_stt_service: STTService | None = None
_llm_service: LLMService | None = None
_tts_service: TTSService | None = None
_orchestrator_service: OrchestratorService | None = None
_db_manager: DatabaseManager | None = None
_conversation_storage_service: ConversationStorageService | None = None


def get_stt_service() -> STTService:
    """Get the STT service instance."""
    if _stt_service is None:
        msg = "STT service not initialized"
        raise RuntimeError(msg)
    return _stt_service


def set_stt_service(service: STTService) -> None:
    """Set the STT service instance."""
    global _stt_service  # noqa: PLW0603
    _stt_service = service


def get_llm_service() -> LLMService:
    """Get the LLM service instance."""
    if _llm_service is None:
        msg = "LLM service not initialized"
        raise RuntimeError(msg)
    return _llm_service


def set_llm_service(service: LLMService) -> None:
    """Set the LLM service instance."""
    global _llm_service  # noqa: PLW0603
    _llm_service = service


def get_tts_service() -> TTSService:
    """Get the TTS service instance."""
    if _tts_service is None:
        msg = "TTS service not initialized"
        raise RuntimeError(msg)
    return _tts_service


def set_tts_service(service: TTSService) -> None:
    """Set the TTS service instance."""
    global _tts_service  # noqa: PLW0603
    _tts_service = service


def get_orchestrator_service() -> OrchestratorService:
    """Get the Orchestrator service instance."""
    if _orchestrator_service is None:
        msg = "Orchestrator service not initialized"
        raise RuntimeError(msg)
    return _orchestrator_service


def set_orchestrator_service(service: OrchestratorService) -> None:
    """Set the Orchestrator service instance."""
    global _orchestrator_service  # noqa: PLW0603
    _orchestrator_service = service


def get_db_manager() -> DatabaseManager:
    """Get the database manager instance."""
    if _db_manager is None:
        msg = "Database manager not initialized"
        raise RuntimeError(msg)
    return _db_manager


def set_db_manager(manager: DatabaseManager) -> None:
    """Set the database manager instance."""
    global _db_manager  # noqa: PLW0603
    _db_manager = manager


def get_conversation_storage_service() -> ConversationStorageService:
    """Get the conversation storage service instance."""
    if _conversation_storage_service is None:
        msg = "Conversation storage service not initialized"
        raise RuntimeError(msg)
    return _conversation_storage_service


def set_conversation_storage_service(service: ConversationStorageService) -> None:
    """Set the conversation storage service instance."""
    global _conversation_storage_service  # noqa: PLW0603
    _conversation_storage_service = service
