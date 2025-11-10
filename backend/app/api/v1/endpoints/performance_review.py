"""Performance Review generation endpoint."""

import logging
import textwrap
import time
import uuid
from typing import Optional
from fastapi import APIRouter, status, Query
from sqlmodel import Session
from fastapi import Depends

from backend.app.models.requests import GenerateReviewRequest
from backend.app.models.responses import GeneratedContentResponse
from backend.app.dependencies import OllamaServiceDep, GroqServiceDep
from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, DocumentType

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/performance-review",
    tags=["Performance Review"]
)


@router.post(
    "/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Performance Review",
    description="Generate comprehensive performance review using AI based on employee achievements and goals",
    responses={
        200: {
            "description": "Successfully generated performance review",
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
async def generate_performance_review(
    request: GenerateReviewRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: Session = Depends(get_session),
    save_to_db: bool = Query(False, description="Save generated document to database"),
    company_id: Optional[int] = Query(None, description="Associate with company profile ID")
) -> GeneratedContentResponse:
    """
    Generate comprehensive performance review based on employee achievements and goals.

    This endpoint uses AI to create a structured performance review including:
    - Overall performance summary
    - Key accomplishments and contributions
    - Skills assessment and development
    - Areas of strength
    - Areas for improvement
    - Goals and development plan
    - Overall rating and recommendations

    **Request Body:**
    - **employee_name**: Name of the employee being reviewed
    - **position**: Employee's job position
    - **review_period**: Review period (e.g., "Q4 2024", "Annual 2024")
    - **achievements**: List of key achievements during the period
    - **skills**: List of skills demonstrated
    - **goals**: List of goals for the next period
    - **rating**: Overall performance rating (0-10)
    - **model_choice**: AI model - "hrcraft_mini" (Ollama, local) or "hrcraft_pro" (Groq, cloud)

    **Returns:**
    - Generated performance review in markdown format
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

    logger.info(
        f"Generating performance review for {request.employee_name}",
        extra={
            "trace_id": trace_id,
            "model_choice": request.model_choice,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "employee_name": request.employee_name,
            "position": request.position,
            "review_period": request.review_period,
            "rating": request.rating
        }
    )

    # Create prompt
    achievements_list = '\n'.join(f"- {achievement}" for achievement in request.achievements)
    skills_list = ', '.join(request.skills)
    goals_list = '\n'.join(f"- {goal}" for goal in request.goals)

    prompt = textwrap.dedent(f"""
        Create a comprehensive performance review for the following employee:

        Employee Name: {request.employee_name}
        Position: {request.position}
        Review Period: {request.review_period}
        Overall Rating: {request.rating}/10

        Key Achievements:
        {achievements_list}

        Skills Demonstrated: {skills_list}

        Goals for Next Period:
        {goals_list}

        Please create a professional performance review document with the following sections:

        1. **Executive Summary** - Brief overview of the employee's performance during the review period.

        2. **Key Accomplishments** - Detailed analysis of the achievements listed above, highlighting
           the impact and value delivered to the organization.

        3. **Skills and Competencies** - Assessment of the skills demonstrated, including:
           - Technical competencies
           - Soft skills and leadership qualities
           - Areas of particular strength

        4. **Performance Analysis** - Detailed evaluation considering:
           - Quality of work
           - Productivity and efficiency
           - Initiative and innovation
           - Collaboration and teamwork
           - Communication skills

        5. **Areas for Development** - Constructive feedback on areas where the employee can improve
           and grow professionally.

        6. **Goals and Development Plan** - Review of the goals set for the next period and suggestions
           for professional development opportunities.

        7. **Overall Assessment** - Summary statement that ties the rating ({request.rating}/10) to
           the performance demonstrated, with recommendations for the future.

        Format the review professionally with clear sections and markdown formatting. Make it balanced,
        constructive, and actionable. The tone should be professional yet supportive.
    """)

    # Generate content using AI service (exceptions will be caught by global handlers)
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    logger.info(
        f"Successfully generated performance review in {generation_time:.2f}s",
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
        title = f"Performance Review: {request.employee_name} - {request.review_period}"
        db_document = GeneratedDocument(
            doc_type=DocumentType.PERFORMANCE_REVIEW,
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
            f"Saved performance review to database (ID: {db_document.id})",
            extra={"trace_id": trace_id, "document_id": db_document.id}
        )

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2),
        id=document_id
    )
