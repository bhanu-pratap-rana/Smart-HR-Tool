"""Offer Letter generation endpoint."""

import logging
import time
import uuid
from typing import Optional
from fastapi import APIRouter, status, Query
from sqlmodel import Session, select
from fastapi import Depends

from backend.app.models.requests import GenerateOfferRequest
from backend.app.models.responses import GeneratedContentResponse
from backend.app.dependencies import OllamaServiceDep, GroqServiceDep
from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, DocumentType, CompanyProfile
from backend.app.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/offer-letter",
    tags=["Offer Letter"]
)


@router.post(
    "/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Offer Letter",
    description="Generate a professional offer letter using AI based on candidate and position details",
    responses={
        200: {
            "description": "Successfully generated offer letter",
            "model": GeneratedContentResponse
        },
        422: {
            "description": "Validation error - invalid input data"
        },
        503: {
            "description": "AI service unavailable"
        },
        500: {
            "description": "Internal server error"
        }
    }
)
async def generate_offer_letter(
    request: GenerateOfferRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: Session = Depends(get_session),
    save_to_db: bool = Query(False, description="Save generated document to database"),
    company_id: Optional[int] = Query(None, description="Associate with company profile ID")
) -> GeneratedContentResponse:
    """
    Generate a professional offer letter based on provided details.

    This endpoint uses AI to create a comprehensive offer letter including:
    - Personalized greeting and congratulations
    - Position details and department
    - Compensation and benefits overview
    - Start date and location information
    - Next steps and acceptance instructions
    - Professional closing

    **Request Body:**
    - **name**: Candidate's full name (e.g., "John Doe")
    - **position**: Job position title (e.g., "Software Engineer")
    - **department**: Department name (e.g., "Engineering")
    - **salary**: Salary details (e.g., "$120,000 per year")
    - **start_date**: Employment start date (e.g., "January 15, 2025")
    - **location**: Work location (e.g., "San Francisco, CA" or "Remote")
    - **model_choice**: AI model - "hrcraft_mini" (Ollama, local) or "hrcraft_pro" (Groq, cloud)

    **Returns:**
    - Generated offer letter in markdown format
    - Model used for generation
    - Generation time in seconds
    - Timestamp of generation
    """
    # Generate unique trace_id for this request
    trace_id = str(uuid.uuid4())
    start_time = time.time()

    # Select appropriate AI service
    service = ollama if request.model_choice == "hrcraft_mini" else groq
    model_info = service.get_model_info()

    # Get company profile for context
    company_profile = session.exec(select(CompanyProfile)).first()

    logger.info(
        f"Generating offer letter for {request.name}",
        extra={
            "trace_id": trace_id,
            "model_choice": request.model_choice,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "candidate_name": request.name,
            "position": request.position,
            "has_company_profile": company_profile is not None
        }
    )

    # Build structured prompt with company context
    prompt_builder = PromptBuilder()
    prompt_data = {
        "name": request.name,
        "position": request.position,
        "department": request.department,
        "salary": request.salary,
        "start_date": request.start_date,
        "location": request.location,
        "reporting_to": request.reporting_to,
        "benefits": request.benefits,
        "special_terms": request.special_terms
    }

    prompt = prompt_builder.build_prompt(
        doc_type="offer_letter",
        data=prompt_data,
        company_profile=company_profile
    )

    # Generate content using AI service (exceptions will be caught by global handlers)
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    logger.info(
        f"Successfully generated offer letter in {generation_time:.2f}s",
        extra={
            "trace_id": trace_id,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "generation_time": generation_time,
            "content_length": len(content)
        }
    )

    # Optionally save to database
    document_id = None
    if save_to_db:
        title = f"Offer Letter: {request.position} - {request.name}"
        db_document = GeneratedDocument(
            doc_type=DocumentType.OFFER_LETTER,
            title=title,
            content=content,
            model_used=model_info["model"],
            generation_time=round(generation_time, 2),
            company_id=company_id
        )
        session.add(db_document)
        session.commit()
        session.refresh(db_document)
        document_id = db_document.id

        logger.info(
            f"Saved offer letter to database (ID: {db_document.id})",
            extra={"trace_id": trace_id, "document_id": db_document.id}
        )

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2),
        id=document_id
    )
