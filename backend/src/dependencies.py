"""Dependency injection for FastAPI."""

from src.services.llm_service import LLMService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService

# Global service instances
_stt_service: STTService | None = None
_llm_service: LLMService | None = None
_tts_service: TTSService | None = None


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
