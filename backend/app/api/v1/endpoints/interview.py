"""Interview Questions generation endpoint."""

import logging
import textwrap
import time
import uuid
from typing import Optional
from fastapi import APIRouter, status, Query
from sqlmodel import Session
from fastapi import Depends

from backend.app.models.requests import GenerateInterviewRequest
from backend.app.models.responses import GeneratedContentResponse
from backend.app.dependencies import OllamaServiceDep, GroqServiceDep
from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, DocumentType

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interview-questions",
    tags=["Interview Questions"]
)


@router.post(
    "/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Interview Questions",
    description="Generate role-specific interview questions using AI to assess technical and soft skills",
    responses={
        200: {
            "description": "Successfully generated interview questions",
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
async def generate_interview_questions(
    request: GenerateInterviewRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: Session = Depends(get_session),
    save_to_db: bool = Query(False, description="Save generated document to database"),
    company_id: Optional[int] = Query(None, description="Associate with company profile ID")
) -> GeneratedContentResponse:
    """
    Generate comprehensive interview questions based on role and skills.

    This endpoint uses AI to create a structured set of interview questions including:
    - Technical questions for each specified skill
    - Behavioral/soft skill questions
    - Situational questions relevant to the role
    - Questions tailored to the experience level
    - Suggested evaluation criteria

    **Request Body:**
    - **role**: Job role being interviewed for (e.g., "Full Stack Developer")
    - **focus_area**: Primary interview focus (e.g., "Backend Development", "System Design")
    - **experience_level**: Years of experience (0-50)
    - **technical_skills**: List of technical skills to assess (e.g., ["Python", "SQL", "Docker"])
    - **soft_skills**: List of soft skills to assess (e.g., ["Communication", "Teamwork"])
    - **model_choice**: AI model - "hrcraft_mini" (Ollama, local) or "hrcraft_pro" (Groq, cloud)

    **Returns:**
    - Generated interview questions in markdown format
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
        f"Generating interview questions for {request.role}",
        extra={
            "trace_id": trace_id,
            "model_choice": request.model_choice,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "role": request.role,
            "focus_area": request.focus_area,
            "experience_level": request.experience_level
        }
    )

    # Create prompt
    prompt = textwrap.dedent(f"""
        Create a comprehensive set of interview questions for the following position:

        Role: {request.role}
        Focus Area: {request.focus_area}
        Experience Level: {request.experience_level} years
        Technical Skills to Assess: {', '.join(request.technical_skills)}
        Soft Skills to Assess: {', '.join(request.soft_skills)}

        Please create a structured interview guide with the following sections:

        1. **Technical Questions** - Create 5-7 technical questions covering the specified skills.
           For each skill, include questions that test both theoretical knowledge and practical application.
           Questions should be appropriate for someone with {request.experience_level} years of experience.

        2. **Problem-Solving & Coding** - Include 2-3 practical problem-solving scenarios or coding challenges
           related to {request.focus_area}. These should be realistic scenarios they might encounter on the job.

        3. **Behavioral Questions** - Create 4-5 behavioral questions using the STAR method to assess
           the specified soft skills: {', '.join(request.soft_skills)}

        4. **Situational Questions** - Include 2-3 situational questions specific to the role that test
           decision-making and judgment in realistic work scenarios.

        5. **Experience & Background** - Add 2-3 questions to understand their relevant experience and
           how it relates to this {request.role} position.

        6. **Evaluation Criteria** - For each section, provide brief guidance on what to look for in
           strong vs. weak answers.

        Format the questions clearly with numbering. Make questions open-ended and designed to generate
        meaningful discussion. Ensure questions are appropriate for a {request.experience_level}-year
        experience level.
    """)

    # Generate content using AI service (exceptions will be caught by global handlers)
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    logger.info(
        f"Successfully generated interview questions in {generation_time:.2f}s",
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
        title = f"Interview Questions: {request.role} - {request.focus_area}"
        db_document = GeneratedDocument(
            doc_type=DocumentType.INTERVIEW_QUESTIONS,
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
            f"Saved interview questions to database (ID: {db_document.id})",
            extra={"trace_id": trace_id, "document_id": db_document.id}
        )

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2),
        id=document_id
    )
