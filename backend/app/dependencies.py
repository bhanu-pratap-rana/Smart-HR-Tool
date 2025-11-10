"""Dependency injection for Smart HR Tool."""

from typing import Annotated
from fastapi import Depends

from backend.app.config import Settings, get_settings
from backend.app.services.ollama_service import OllamaService
from backend.app.services.groq_service import GroqService


# ============================================================================
# Settings Dependency
# ============================================================================

SettingsDep = Annotated[Settings, Depends(get_settings)]


# ============================================================================
# Service Dependencies
# ============================================================================

def get_ollama_service(settings: SettingsDep) -> OllamaService:
    """
    Get Ollama service instance.

    Args:
        settings: Application settings

    Returns:
        OllamaService: Configured Ollama service
    """
    return OllamaService(settings)


def get_groq_service(settings: SettingsDep) -> GroqService:
    """
    Get Groq service instance.

    Args:
        settings: Application settings

    Returns:
        GroqService: Configured Groq service
    """
    return GroqService(settings)


# Type aliases for cleaner dependency injection
OllamaServiceDep = Annotated[OllamaService, Depends(get_ollama_service)]
GroqServiceDep = Annotated[GroqService, Depends(get_groq_service)]


# ============================================================================
# AI Service Selector
# ============================================================================

def get_ai_service(
    model_choice: str,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep
):
    """
    Get appropriate AI service based on model choice.

    Args:
        model_choice: 'bytical_mini' for Ollama or 'bytical_versatile' for Groq
        ollama: Ollama service instance
        groq: Groq service instance

    Returns:
        AI service instance (OllamaService or GroqService)
    """
    if model_choice == "bytical_mini":
        return ollama
    return groq


# Export commonly used dependencies
__all__ = [
    "SettingsDep",
    "OllamaServiceDep",
    "GroqServiceDep",
    "get_ollama_service",
    "get_groq_service",
    "get_ai_service",
]
