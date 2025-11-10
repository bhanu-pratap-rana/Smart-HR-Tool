"""Retry logic with exponential backoff for AI services."""

import logging
from typing import TypeVar, Callable
from functools import wraps

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
):
    """
    Decorator for retrying AI generation with exponential backoff.

    This decorator automatically retries failed AI service calls with
    exponential backoff between attempts. It handles transient errors
    like connection failures and timeouts, but does not retry on
    authentication or validation errors.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        min_wait: Minimum wait time in seconds between retries (default: 1)
        max_wait: Maximum wait time in seconds between retries (default: 10)

    Returns:
        Decorated function with retry logic

    Example:
        ```python
        from backend.app.core.retry import with_retry
        from backend.app.core.exceptions import GroqAPIError

        class GroqService:
            @with_retry(max_attempts=3)
            def generate(self, prompt: str) -> str:
                # This will retry on transient errors
                return self.client.chat.completions.create(...)
        ```

    Note:
        - Does NOT retry on authentication errors (invalid API keys)
        - Does NOT retry on validation errors (bad input)
        - DOES retry on connection errors, timeouts, and API errors
        - Rate limit errors are NOT retried (handled separately)
    """
    # Import here to avoid circular dependencies
    try:
        import groq
        from backend.app.core.exceptions import (
            OllamaConnectionError,
            OllamaTimeoutError,
            GroqAPIError
        )

        # Define retryable exceptions
        retryable_exceptions = (
            groq.APIConnectionError,
            groq.APITimeoutError,
            ConnectionError,
            OllamaConnectionError,
            OllamaTimeoutError,
            TimeoutError
        )
    except ImportError:
        # Fallback if groq not installed
        from backend.app.core.exceptions import (
            OllamaConnectionError,
            OllamaTimeoutError
        )
        retryable_exceptions = (
            ConnectionError,
            OllamaConnectionError,
            OllamaTimeoutError,
            TimeoutError
        )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(
                multiplier=1,
                min=min_wait,
                max=max_wait
            ),
            retry=retry_if_exception_type(retryable_exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )
        def wrapper(*args, **kwargs) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_groq_retry(max_attempts: int = 3):
    """
    Specialized retry decorator for Groq API calls.

    This is a convenience wrapper around `with_retry` tuned for Groq's
    API characteristics. It handles Groq-specific transient errors but
    lets authentication and rate limit errors pass through immediately.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)

    Returns:
        Decorated function with Groq-specific retry logic

    Example:
        ```python
        from backend.app.core.retry import with_groq_retry

        class GroqService:
            @with_groq_retry(max_attempts=3)
            def generate(self, prompt: str) -> str:
                return self.client.chat.completions.create(...)
        ```
    """
    try:
        import groq
        from backend.app.core.exceptions import GroqAuthenticationError, GroqRateLimitError

        # Groq-specific retryable exceptions
        retryable_exceptions = (
            groq.APIConnectionError,
            groq.APITimeoutError,
            ConnectionError,
            TimeoutError
        )

        # Exceptions that should NOT be retried
        non_retryable_exceptions = (
            groq.AuthenticationError,
            groq.RateLimitError,
            GroqAuthenticationError,
            GroqRateLimitError
        )

    except ImportError:
        # Fallback
        retryable_exceptions = (ConnectionError, TimeoutError)
        non_retryable_exceptions = ()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(retryable_exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )
        def wrapper(*args, **kwargs) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def with_ollama_retry(max_attempts: int = 3):
    """
    Specialized retry decorator for Ollama API calls.

    This is a convenience wrapper around `with_retry` tuned for Ollama's
    local service characteristics. It retries on connection and timeout
    errors, which are common when Ollama is starting up or under load.

    Args:
        max_attempts: Maximum number of retry attempts (default: 3)

    Returns:
        Decorated function with Ollama-specific retry logic

    Example:
        ```python
        from backend.app.core.retry import with_ollama_retry

        class OllamaService:
            @with_ollama_retry(max_attempts=3)
            def generate(self, prompt: str) -> str:
                return requests.post(self.url, json=payload)
        ```
    """
    from backend.app.core.exceptions import (
        OllamaConnectionError,
        OllamaTimeoutError
    )

    retryable_exceptions = (
        OllamaConnectionError,
        OllamaTimeoutError,
        ConnectionError,
        TimeoutError
    )

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=15),  # Longer waits for local service
            retry=retry_if_exception_type(retryable_exceptions),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )
        def wrapper(*args, **kwargs) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator
