"""Ollama AI service for local model generation."""

import logging
import requests
from typing import Dict, Any

from backend.app.config import Settings
from backend.app.core.exceptions import (
    OllamaConnectionError,
    OllamaGenerationError,
    OllamaTimeoutError
)
from backend.app.core.retry import with_ollama_retry

logger = logging.getLogger(__name__)


class OllamaService:
    """Service for interacting with Ollama local AI models."""

    def __init__(self, settings: Settings):
        """
        Initialize Ollama service.

        Args:
            settings: Application settings containing Ollama configuration
        """
        self.settings = settings
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens

    @with_ollama_retry(max_attempts=3)
    def generate(self, prompt: str) -> str:
        """
        Generate content using Ollama local model with automatic retry.

        This method uses exponential backoff retry logic for transient errors
        (connection failures, timeouts). This is useful when Ollama is starting
        up or temporarily under load.

        Args:
            prompt: Text prompt for generation

        Returns:
            str: Generated content

        Raises:
            OllamaConnectionError: If Ollama service is unreachable after retries
            OllamaTimeoutError: If request times out after retries
            OllamaGenerationError: If generation fails after retries
        """
        try:
            logger.info(f"Generating content with Ollama model: {self.model}")

            url = f"{self.base_url}/api/generate"
            payload: Dict[str, Any] = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }

            response = requests.post(
                url,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            result = response.json()

            if "response" not in result:
                raise OllamaGenerationError("Invalid response format from Ollama")

            generated_text = result["response"]

            logger.info(f"Successfully generated {len(generated_text)} characters")

            return generated_text

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            raise OllamaConnectionError(
                f"Cannot connect to Ollama service at {self.base_url}. "
                f"Please ensure Ollama is running."
            )

        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timeout: {e}")
            raise OllamaTimeoutError()

        except requests.exceptions.HTTPError as e:
            logger.error(f"Ollama HTTP error: {e}")
            status_code = e.response.status_code if e.response else "unknown"
            raise OllamaGenerationError(
                f"HTTP {status_code} error from Ollama service"
            )

        except KeyError as e:
            logger.error(f"Invalid Ollama response format: {e}")
            raise OllamaGenerationError(
                "Invalid response format from Ollama"
            )

        except Exception as e:
            logger.error(f"Unexpected Ollama error: {e}")
            raise OllamaGenerationError(str(e))

    def health_check(self) -> bool:
        """
        Check if Ollama service is available.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Ollama model.

        Returns:
            dict: Model information
        """
        return {
            "provider": "Ollama",
            "model": self.model,
            "type": "local",
            "base_url": self.base_url,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
