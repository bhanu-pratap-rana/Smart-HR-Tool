"""AI generation services for Smart HR Tool."""

from .ollama_service import OllamaService
from .groq_service import GroqService

__all__ = ["OllamaService", "GroqService"]
