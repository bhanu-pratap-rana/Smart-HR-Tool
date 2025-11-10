"""Response models for API endpoints."""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid


class GeneratedContentResponse(BaseModel):
    """Response model for AI-generated content."""

    content: str = Field(..., description="Generated content")
    model_used: str = Field(..., description="AI model used for generation")
    generation_time: Optional[float] = Field(None, description="Generation time in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    id: Optional[int] = Field(None, description="Database document ID (only when save_to_db=true)")

    model_config = ConfigDict(
        protected_namespaces=(),  # Fix warning about 'model_' namespace
        json_schema_extra={
            "example": {
                "content": "# Software Engineer\\n\\n## About the Role\\n\\nWe are seeking...",
                "model_used": "deepseek-r1:8b",
                "generation_time": 2.5,
                "timestamp": "2025-11-07T12:00:00Z",
                "id": 42
            }
        }
    )


class ModelInfoResponse(BaseModel):
    """Response model for model information."""

    provider: str = Field(..., description="Model provider (Ollama/Groq)")
    model: str = Field(..., description="Model name")
    type: str = Field(..., description="Model type (local/cloud)")
    temperature: float = Field(..., description="Generation temperature")
    max_tokens: int = Field(..., description="Maximum tokens")
    available: bool = Field(default=True, description="Model availability status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "Ollama",
                "model": "deepseek-r1:8b",
                "type": "local",
                "temperature": 0.7,
                "max_tokens": 2000,
                "available": True
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(default="healthy", description="Service status")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Environment (development/staging/production)")
    services: Dict[str, Any] = Field(
        default_factory=dict,
        description="External services status"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "development",
                "services": {
                    "ollama": {
                        "available": True,
                        "model": "deepseek-r1:8b"
                    },
                    "groq": {
                        "available": True,
                        "model": "llama-3.3-70b-versatile"
                    }
                },
                "timestamp": "2025-11-07T12:00:00Z"
            }
        }
    )


class ErrorDetail(BaseModel):
    """Detailed error information following best practices."""

    code: str = Field(..., description="Error code for programmatic handling")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field name if validation error")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "GROQ_API_ERROR",
                "message": "Failed to connect to Groq service",
                "field": None
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Standard error response with traceability.

    Provides structured error information with a unique trace_id for debugging
    and support purposes. This follows REST API best practices for error handling.
    """

    error: ErrorDetail = Field(..., description="Error details")
    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique trace ID for error tracking"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "GROQ_API_ERROR",
                    "message": "Failed to connect to Groq service",
                    "field": None
                },
                "trace_id": "abc-123-def-456",
                "timestamp": "2025-11-07T12:00:00Z"
            }
        }
    )
