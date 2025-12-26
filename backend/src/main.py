"""FastAPI application entry point for Local Voice Assistant Backend."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import __version__
from src.api.config import router as config_router
from src.api.conversations import router as conversations_router
from src.api.health import router as health_router
from src.api.llm import router as llm_router
from src.api.orchestrator import router as orchestrator_router
from src.api.stt import router as stt_router
from src.api.tts import router as tts_router
from src.api.websocket import router as websocket_router
from src.config import CONVERSATION_DB_PATH
from src.db.database import DatabaseManager
from src.dependencies import (
    set_conversation_storage_service,
    set_db_manager,
    set_llm_service,
    set_orchestrator_service,
    set_stt_service,
    set_tts_service,
)
from src.models.config import settings
from src.services.conversation_storage_service import ConversationStorageService
from src.services.llm_service import LLMService
from src.services.orchestrator_service import OrchestratorService
from src.services.stt_service import STTService
from src.services.tts_service import TTSService

logger = logging.getLogger(__name__)


def validate_startup_config() -> list[str]:
    """Validate critical configuration on startup.

    Returns:
        List of warning messages for non-critical issues.

    Raises:
        RuntimeError: If critical configuration is missing.
    """
    warnings: list[str] = []

    # Check TTS model path
    if not settings.tts.model_path.exists():
        warnings.append(
            f"TTS model path does not exist: {settings.tts.model_path}. "
            "TTS service will fail to load."
        )

    # Check API keys (warn if empty, don't fail)
    if not settings.openai.api_key.get_secret_value():
        warnings.append(
            "OPENAI_API_KEY is not set. LLM features will be unavailable."
        )

    if not settings.deepgram.api_key.get_secret_value():
        warnings.append(
            "DEEPGRAM_API_KEY is not set. "
            "Deepgram-based STT features will be unavailable."
        )

    return warnings


def log_startup_config() -> None:
    """Log current configuration with masked secrets."""
    logger.info("=== Application Configuration ===")
    logger.info("Log Level: %s", settings.log_level)
    logger.info("Debug Mode: %s", settings.debug)

    # TTS Configuration
    logger.info("TTS Model Path: %s", settings.tts.model_path)
    logger.info("TTS Device: %s", settings.tts.device)
    logger.info("TTS Max Concurrent: %d", settings.tts.max_concurrent)

    # OpenAI Configuration (mask API key)
    openai_key = settings.openai.api_key.get_secret_value()
    key_status = "configured" if openai_key else "not set"
    logger.info("OpenAI API Key: %s", key_status)
    logger.info("OpenAI Model: %s", settings.openai.model)
    if settings.openai.base_url:
        logger.info("OpenAI Base URL: %s", settings.openai.base_url)

    # Deepgram Configuration (mask API key)
    deepgram_key = settings.deepgram.api_key.get_secret_value()
    key_status = "configured" if deepgram_key else "not set"
    logger.info("Deepgram API Key: %s", key_status)
    logger.info("Deepgram Model: %s", settings.deepgram.model)

    # Orchestrator Configuration
    logger.info("Orchestrator Timeout: %.1fs", settings.orchestrator.timeout)
    logger.info(
        "Orchestrator Max Concurrent: %d", settings.orchestrator.max_concurrent
    )

    logger.info("=== End Configuration ===")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - load models on startup."""
    # Validate configuration and log warnings
    warnings = validate_startup_config()
    for warning in warnings:
        logger.warning(warning)

    # Log current configuration
    log_startup_config()

    # Initialize database
    db_manager = DatabaseManager(CONVERSATION_DB_PATH)
    await db_manager.initialize()
    set_db_manager(db_manager)

    # Initialize conversation storage service
    storage_service = ConversationStorageService(db_manager)
    set_conversation_storage_service(storage_service)

    # Initialize STT service
    stt_service = STTService()
    set_stt_service(stt_service)
    await stt_service.load_model()

    # Initialize LLM service
    llm_service = LLMService()
    set_llm_service(llm_service)

    # Initialize TTS service
    tts_service = TTSService()
    set_tts_service(tts_service)
    try:
        await tts_service.load_model()
    except Exception as e:
        # Log but don't fail startup - status endpoint will show unhealthy
        logger.warning("Failed to load TTS model: %s", e)

    # Initialize Orchestrator service
    orchestrator_service = OrchestratorService(
        stt_service=stt_service,
        llm_service=llm_service,
        tts_service=tts_service,
        storage_service=storage_service,
    )
    set_orchestrator_service(orchestrator_service)

    yield
    # Cleanup on shutdown
    await db_manager.close()


app = FastAPI(
    title="Local Voice Assistant API",
    description="Backend API for the Local Voice Assistant",
    version=__version__,
    lifespan=lifespan,
)

# Configure CORS for development
# Allow frontend on localhost:3000 to access the API
# TODO: For production, restrict origins to actual domain and limit methods/headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(stt_router)
app.include_router(llm_router)
app.include_router(tts_router)
app.include_router(orchestrator_router)
app.include_router(conversations_router)
app.include_router(websocket_router)
app.include_router(config_router)
