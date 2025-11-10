"""Pydantic models for Smart HR Tool."""

from .requests import (
    BaseRequest,
    GenerateJDRequest,
    GenerateInterviewRequest,
    GenerateOfferRequest,
    GenerateOnboardingRequest,
    GenerateReviewRequest
)
from .responses import (
    GeneratedContentResponse,
    HealthCheckResponse,
    ModelInfoResponse
)

__all__ = [
    # Request models
    "BaseRequest",
    "GenerateJDRequest",
    "GenerateInterviewRequest",
    "GenerateOfferRequest",
    "GenerateOnboardingRequest",
    "GenerateReviewRequest",
    # Response models
    "GeneratedContentResponse",
    "HealthCheckResponse",
    "ModelInfoResponse",
]
