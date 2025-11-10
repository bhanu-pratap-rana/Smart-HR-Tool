"""Groq AI service for cloud-based model generation."""

import logging
import groq
from typing import Dict, Any

from backend.app.config import Settings
from backend.app.core.exceptions import (
    GroqAPIError,
    GroqAuthenticationError,
    GroqRateLimitError
)
from backend.app.core.retry import with_groq_retry

logger = logging.getLogger(__name__)


class GroqService:
    """Service for interacting with Groq cloud AI models."""

    def __init__(self, settings: Settings):
        """
        Initialize Groq service with cached client.

        Args:
            settings: Application settings containing Groq configuration

        Raises:
            GroqAuthenticationError: If GROQ_API_KEY is not set
        """
        self.settings = settings
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens

        if not self.api_key:
            raise GroqAuthenticationError("GROQ_API_KEY is not set")

        # Cache the Groq client instance
        self.client = groq.Groq(api_key=self.api_key)
        logger.info(f"Initialized Groq service with model: {self.model}")

    @with_groq_retry(max_attempts=3)
    def generate(self, prompt: str) -> str:
        """
        Generate content using Groq cloud model with automatic retry.

        This method uses exponential backoff retry logic for transient errors
        (connection failures, timeouts). Authentication and rate limit errors
        are not retried and will fail immediately.

        Args:
            prompt: Text prompt for generation

        Returns:
            str: Generated content

        Raises:
            GroqAuthenticationError: If API key is invalid (not retried)
            GroqRateLimitError: If rate limit is exceeded (not retried)
            GroqAPIError: If generation fails after retries
        """
        try:
            logger.info(f"Generating content with Groq model: {self.model}")

            # Use the cached client instance
            completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            if not completion.choices:
                raise GroqAPIError("No completion choices returned")

            generated_text = completion.choices[0].message.content

            if not generated_text:
                raise GroqAPIError("Empty response from Groq API")

            logger.info(f"Successfully generated {len(generated_text)} characters")

            return generated_text

        except groq.AuthenticationError as e:
            logger.error(f"Groq authentication error: {e}")
            raise GroqAuthenticationError(
                "Invalid Groq API key. Please check your GROQ_API_KEY"
            )

        except groq.RateLimitError as e:
            logger.error(f"Groq rate limit exceeded: {e}")
            raise GroqRateLimitError(retry_after=60)

        except groq.APIConnectionError as e:
            logger.error(f"Groq API connection error: {e}")
            raise GroqAPIError(
                "Cannot connect to Groq API. Please check your internet connection."
            )

        except groq.APIError as e:
            logger.error(f"Groq API error: {e}")
            raise GroqAPIError(str(e))

        except Exception as e:
            logger.error(f"Unexpected Groq error: {e}")
            raise GroqAPIError(f"Unexpected error: {str(e)}")

    def health_check(self) -> Dict[str, Any]:
        """
        Check if Groq service is available.

        Returns:
            dict: Service health status with availability and model info
        """
        try:
            # Try a simple generation to test connectivity using cached client
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=5
            )
            return {
                "available": bool(completion.choices),
                "model": self.model,
                "provider": "Groq"
            }
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")
            return {
                "available": False,
                "model": self.model,
                "provider": "Groq",
                "error": str(e)
            }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current Groq model.

        Returns:
            dict: Model information
        """
        return {
            "provider": "Groq",
            "model": self.model,
            "type": "cloud",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
