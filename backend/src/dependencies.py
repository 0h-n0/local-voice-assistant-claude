"""Dependency injection for FastAPI."""

from src.services.stt_service import STTService

# Global STT service instance
_stt_service: STTService | None = None


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
