"""Main FastAPI application for Smart HR Tool."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import get_settings
from backend.app.core.exceptions import (
    SmartHRException,
    smart_hr_exception_handler,
    generic_exception_handler
)
from backend.app.api.v1.router import api_router
from backend.app.models.responses import HealthCheckResponse
from backend.app.dependencies import get_ollama_service, get_groq_service
from backend.app.database import create_db_and_tables

# Initialize settings
settings = get_settings()

# Configure JSON logging
from backend.app.utils.logging import setup_json_logging

# Use JSON logging in production, standard format in development
setup_json_logging(
    level=getattr(logging, settings.log_level),
    format_as_json=settings.environment != "development"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database tables
    create_db_and_tables()

    # Store settings in app state
    app.state.settings = settings

    yield

    # Shutdown
    logger.info("Shutting down application")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    # Smart HR Tool API

    AI-powered HR assistant for generating professional HR documents.

    ## Features

    * 🎯 **Job Description Generation** - Create professional job descriptions
    * 💼 **Offer Letter Creation** - Generate personalized offer letters
    * 📋 **Interview Questions** - Create role-specific interview questions
    * 🚀 **Onboarding Plans** - Design comprehensive onboarding experiences
    * ⭐ **Performance Reviews** - Generate detailed performance evaluations

    ## AI Models

    * **HRCraft Mini** - Ollama (deepseek-r1:8b) - Local, fast, free
    * **HRCraft Pro** - Groq (llama-3.3-70b) - Cloud, powerful, fast

    ## Authentication

    No authentication required for development environment.

    ## Rate Limiting

    Development: 60 requests/minute per IP
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.debug
)

# ============================================================================
# Middleware
# ============================================================================

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================

app.add_exception_handler(SmartHRException, smart_hr_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# ============================================================================
# Routers
# ============================================================================

# Include API v1 router
app.include_router(api_router, prefix=settings.api_prefix)

# ============================================================================
# Root Endpoints
# ============================================================================

@app.get(
    "/",
    include_in_schema=False
)
async def root():
    """Root endpoint - redirect to docs."""
    return JSONResponse(
        content={
            "message": f"Welcome to {settings.app_name}!",
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/health"
        }
    )


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health Check",
    description="Check the health status of the application and external services"
)
async def health_check() -> HealthCheckResponse:
    """
    Check application health and external services status.

    Returns:
        HealthCheckResponse: Service health information
    """
    # Check Ollama service
    ollama_service = get_ollama_service(settings)
    ollama_healthy = ollama_service.health_check()

    # Check Groq service
    try:
        groq_service = get_groq_service(settings)
        groq_healthy = groq_service.health_check()
    except Exception as e:
        logger.warning(f"Groq health check failed: {e}")
        groq_healthy = False

    services_status = {
        "ollama": {
            "available": ollama_healthy,
            "model": settings.ollama_model,
            "url": settings.ollama_base_url
        },
        "groq": {
            "available": groq_healthy,
            "model": settings.groq_model
        }
    }

    return HealthCheckResponse(
        status="healthy" if (ollama_healthy or groq_healthy) else "degraded",
        version=settings.app_version,
        environment=settings.environment,
        services=services_status
    )


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development(),
        log_level=settings.log_level.lower()
    )
