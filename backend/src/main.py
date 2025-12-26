"""FastAPI application entry point for Local Voice Assistant Backend."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import __version__
from src.api.health import router as health_router
from src.api.llm import router as llm_router
from src.api.stt import router as stt_router
from src.dependencies import set_llm_service, set_stt_service
from src.services.llm_service import LLMService
from src.services.stt_service import STTService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan - load models on startup."""
    # Initialize STT service
    stt_service = STTService()
    set_stt_service(stt_service)
    await stt_service.load_model()

    # Initialize LLM service
    llm_service = LLMService()
    set_llm_service(llm_service)

    yield
    # Cleanup on shutdown if needed


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
