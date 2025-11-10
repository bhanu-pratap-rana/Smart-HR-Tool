"""Main API v1 router combining all endpoints."""

from fastapi import APIRouter

from backend.app.api.v1.endpoints import (
    job_description,
    company,
    documents,
    offer_letter,
    interview,
    onboarding,
    export,
    performance_review
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(company.router)
api_router.include_router(documents.router)
api_router.include_router(job_description.router)
api_router.include_router(offer_letter.router)
api_router.include_router(interview.router)
api_router.include_router(onboarding.router)
api_router.include_router(performance_review.router)
api_router.include_router(export.router)
