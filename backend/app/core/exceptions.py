"""Custom exceptions for Smart HR Tool."""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from backend.app.models.responses import ErrorResponse, ErrorDetail


class SmartHRException(HTTPException):
    """Base exception for Smart HR Tool with structured error responses."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# ============================================================================
# Ollama Service Exceptions
# ============================================================================

class OllamaConnectionError(SmartHRException):
    """
    Raised when Ollama service is unreachable.

    This typically indicates that Ollama is not running or not accessible
    at the configured URL.
    """

    def __init__(self, detail: str = "Ollama service is not running or not accessible"):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="OLLAMA_CONNECTION_ERROR"
        )


class OllamaGenerationError(SmartHRException):
    """
    Raised when Ollama generation fails.

    This can occur due to invalid prompts, timeouts, or internal Ollama errors.
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ollama generation failed: {detail}",
            error_code="OLLAMA_GENERATION_ERROR"
        )


class OllamaTimeoutError(SmartHRException):
    """Raised when Ollama request times out."""

    def __init__(self, timeout_seconds: int = 120):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Ollama request timeout after {timeout_seconds} seconds",
            error_code="OLLAMA_TIMEOUT"
        )


# ============================================================================
# Groq API Exceptions
# ============================================================================

class GroqAPIError(SmartHRException):
    """
    Raised when Groq API request fails.

    This is a general error for Groq API failures.
    """

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Groq API error: {detail}",
            error_code="GROQ_API_ERROR"
        )


class GroqAuthenticationError(SmartHRException):
    """
    Raised when Groq API key is invalid or missing.

    Check your GROQ_API_KEY environment variable.
    """

    def __init__(self, detail: str = "Invalid or missing Groq API key"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="GROQ_AUTH_ERROR"
        )


class GroqRateLimitError(SmartHRException):
    """
    Raised when Groq API rate limit is exceeded.

    Wait before making more requests or upgrade your Groq plan.
    """

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Groq API rate limit exceeded. Retry after {retry_after} seconds",
            error_code="GROQ_RATE_LIMIT",
            headers={"Retry-After": str(retry_after)}
        )


# ============================================================================
# Application Exceptions
# ============================================================================

class ValidationError(SmartHRException):
    """Raised when request validation fails."""

    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )


class ResourceNotFoundError(SmartHRException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} with ID '{resource_id}' not found",
            error_code="RESOURCE_NOT_FOUND"
        )


class RateLimitExceededError(SmartHRException):
    """
    Raised when API rate limit is exceeded.

    This is for application-level rate limiting, not Groq API limits.
    """

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Retry after {retry_after} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": str(retry_after)}
        )


# ============================================================================
# Exception Handlers
# ============================================================================

async def smart_hr_exception_handler(
    request: Request,
    exc: SmartHRException
) -> JSONResponse:
    """
    Custom exception handler for SmartHRException with trace_id.

    Returns structured JSON error responses with:
    - error_code: Machine-readable error code
    - message: Human-readable error message
    - trace_id: Unique identifier for tracking the error
    - timestamp: ISO timestamp of the error

    Args:
        request: FastAPI request object
        exc: SmartHRException instance

    Returns:
        JSONResponse with structured error details including trace_id
    """
    trace_id = str(uuid.uuid4())

    error_response = ErrorResponse(
        error=ErrorDetail(
            code=exc.error_code,
            message=exc.detail
        ),
        trace_id=trace_id
    )

    # Log the error with trace_id
    import logging
    logger = logging.getLogger(__name__)
    logger.error(
        f"SmartHR Exception: {exc.error_code} - {exc.detail}",
        extra={"trace_id": trace_id, "path": str(request.url.path)}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json'),
        headers=exc.headers
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handler for unexpected exceptions with trace_id.

    Catches any unhandled exceptions and returns a generic error response
    with unique trace_id for debugging.

    Args:
        request: FastAPI request object
        exc: Exception instance

    Returns:
        JSONResponse with generic error message and trace_id
    """
    trace_id = str(uuid.uuid4())

    # Include exception details only in debug mode
    message = "An unexpected error occurred. Please try again later."
    if hasattr(request.app.state, 'settings') and request.app.state.settings.debug:
        message = f"{message} Details: {str(exc)}"

    error_response = ErrorResponse(
        error=ErrorDetail(
            code="INTERNAL_SERVER_ERROR",
            message=message
        ),
        trace_id=trace_id
    )

    # Log the error with trace_id and full exception
    import logging
    logger = logging.getLogger(__name__)
    logger.exception(
        f"Unhandled exception: {type(exc).__name__}",
        extra={"trace_id": trace_id, "path": str(request.url.path)},
        exc_info=exc
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json')
    )


# Export all exceptions
__all__ = [
    "SmartHRException",
    "OllamaConnectionError",
    "OllamaGenerationError",
    "OllamaTimeoutError",
    "GroqAPIError",
    "GroqAuthenticationError",
    "GroqRateLimitError",
    "ValidationError",
    "ResourceNotFoundError",
    "RateLimitExceededError",
    "smart_hr_exception_handler",
    "generic_exception_handler",
]
