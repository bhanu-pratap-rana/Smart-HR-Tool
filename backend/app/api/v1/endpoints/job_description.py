"""Job Description generation endpoint."""

import logging
import time
import uuid
from typing import Optional
from fastapi import APIRouter, status, Depends, Query
from sqlmodel import Session, select

from backend.app.models.requests import GenerateJDRequest
from backend.app.models.responses import GeneratedContentResponse
from backend.app.dependencies import OllamaServiceDep, GroqServiceDep
from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, DocumentType, CompanyProfile
from backend.app.services.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/job-description",
    tags=["Job Description"]
)


@router.post(
    "/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Job Description",
    description="Generate a professional job description using AI based on provided requirements",
    responses={
        200: {
            "description": "Successfully generated job description",
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
async def generate_job_description(
    request: GenerateJDRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: Session = Depends(get_session),
    save_to_db: bool = Query(False, description="Save generated document to database"),
    company_id: Optional[int] = Query(None, description="Associate with company profile ID")
) -> GeneratedContentResponse:
    """
    Generate a professional job description based on provided details.

    This endpoint uses AI to create a comprehensive job description including:
    - Role overview and responsibilities
    - Required qualifications and experience
    - Skills and competencies
    - Compensation and benefits
    - Application process

    **Request Body:**
    - **job_title**: Position title (e.g., "Senior Python Developer")
    - **department**: Department name (e.g., "Engineering")
    - **exp_level**: Years of experience required (0-50)
    - **qualification**: Required qualifications (e.g., "Bachelor's in CS")
    - **req_skills**: List of required skills (e.g., ["Python", "FastAPI"])
    - **role**: Role description and key responsibilities
    - **salary**: Salary range (e.g., "$100k-150k")
    - **location**: Job location (e.g., "Remote" or "San Francisco, CA")
    - **model_choice**: AI model - "hrcraft_mini" (Ollama, local) or "hrcraft_pro" (Groq, cloud)

    **Returns:**
    - Generated job description in markdown format
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
        f"Generating job description for {request.job_title}",
        extra={
            "trace_id": trace_id,
            "model_choice": request.model_choice,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "job_title": request.job_title,
            "department": request.department,
            "has_company_profile": company_profile is not None
        }
    )

    # Build structured prompt with company context
    prompt_builder = PromptBuilder()
    prompt_data = {
        "job_title": request.job_title,
        "department": request.department,
        "exp_level": request.exp_level,
        "qualification": request.qualification,
        "req_skills": ', '.join(request.req_skills),
        "req_skills_list": request.req_skills,  # For template loop
        "role": request.role,
        "salary": request.salary,
        "location": request.location
    }

    prompt = prompt_builder.build_prompt(
        doc_type="job_description",
        data=prompt_data,
        company_profile=company_profile
    )

    # Generate content using AI service (exceptions will be caught by global handlers)
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    logger.info(
        f"Successfully generated job description in {generation_time:.2f}s",
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
        title = f"Job Description: {request.job_title} - {request.department}"
        db_document = GeneratedDocument(
            doc_type=DocumentType.JOB_DESCRIPTION,
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
            f"Saved job description to database (ID: {db_document.id})",
            extra={"trace_id": trace_id, "document_id": db_document.id}
        )

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2),
        id=document_id
    )
