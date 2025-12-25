"""FastAPI application entry point for Local Voice Assistant Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.health import router as health_router

app = FastAPI(
    title="Local Voice Assistant API",
    description="Backend API for the Local Voice Assistant",
    version="0.1.0",
)

# Configure CORS for development
# Allow frontend on localhost:3000 to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
