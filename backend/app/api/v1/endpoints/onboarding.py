"""Onboarding Plan generation endpoint."""

import logging
import textwrap
import time
import uuid
from typing import Optional
from fastapi import APIRouter, status, Query
from sqlmodel import Session
from fastapi import Depends

from backend.app.models.requests import GenerateOnboardingRequest
from backend.app.models.responses import GeneratedContentResponse
from backend.app.dependencies import OllamaServiceDep, GroqServiceDep
from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, DocumentType

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/onboarding-plan",
    tags=["Onboarding Plan"]
)


@router.post(
    "/generate",
    response_model=GeneratedContentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Onboarding Plan",
    description="Generate a comprehensive onboarding plan using AI to structure the new hire experience",
    responses={
        200: {
            "description": "Successfully generated onboarding plan",
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
async def generate_onboarding_plan(
    request: GenerateOnboardingRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: Session = Depends(get_session),
    save_to_db: bool = Query(False, description="Save generated document to database"),
    company_id: Optional[int] = Query(None, description="Associate with company profile ID")
) -> GeneratedContentResponse:
    """
    Generate a comprehensive onboarding plan for new hires.

    This endpoint uses AI to create a structured onboarding plan including:
    - Week-by-week or day-by-day schedule
    - Skills development roadmap
    - Tools and systems training
    - Team introductions and meetings
    - Goals and milestones for each phase
    - Resources and documentation to review

    **Request Body:**
    - **position**: Job position (e.g., "Frontend Developer")
    - **department**: Department name (e.g., "Engineering")
    - **duration**: Onboarding duration in days (e.g., 30, 60, 90)
    - **arrangement**: Work arrangement ("Remote", "Hybrid", or "Onsite")
    - **skills**: List of skills to develop (e.g., ["React", "TypeScript", "Testing"])
    - **tools**: List of tools/systems to learn (e.g., ["GitHub", "Jira", "Figma"])
    - **model_choice**: AI model - "hrcraft_mini" (Ollama, local) or "hrcraft_pro" (Groq, cloud)

    **Returns:**
    - Generated onboarding plan in markdown format
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
        f"Generating onboarding plan for {request.position}",
        extra={
            "trace_id": trace_id,
            "model_choice": request.model_choice,
            "model_name": model_info["model"],
            "provider": model_info["provider"],
            "position": request.position,
            "department": request.department,
            "duration": request.duration
        }
    )

    # Create prompt
    prompt = textwrap.dedent(f"""
        Create a comprehensive {request.duration}-day onboarding plan for a new hire in the following role:

        Position: {request.position}
        Department: {request.department}
        Duration: {request.duration} days
        Work Arrangement: {request.arrangement}
        Skills to Develop: {', '.join(request.skills)}
        Tools/Systems to Learn: {', '.join(request.tools)}
        Include Company Culture Section: {"Yes" if request.include_culture else "No"}
        Include Mentorship Program: {"Yes" if request.include_mentorship else "No"}

        Please create a detailed, structured onboarding plan with the following sections:

        1. **Overview & Objectives**
           - Welcome message and onboarding goals
           - What success looks like at 30/60/90 days (adjust based on {request.duration}-day duration)
           - Key stakeholders and points of contact

        2. **Pre-Start Preparation** (Before Day 1)
           - Equipment and access setup
           - Pre-reading materials and resources
           - Administrative tasks to complete

        3. **Week-by-Week Breakdown** (or Day-by-Day if duration < 30 days)
           Break down the {request.duration} days into logical phases:
           - First Week/Days: Orientation, team introductions, environment setup
           - Following Weeks: Progressive skill development, project involvement
           - Final Week: Independence, contribution, feedback sessions

           For each phase, include:
           - Goals and milestones
           - Training sessions on specific tools: {', '.join(request.tools)}
           - Skills development activities for: {', '.join(request.skills)}
           - Team meetings and 1-on-1s
           - Hands-on projects or tasks
           - Check-in points and assessments

        4. **Skills Development Roadmap**
           For each skill in [{', '.join(request.skills)}]:
           - Learning resources and documentation
           - Hands-on exercises and projects
           - Expected proficiency timeline
           - Assessment criteria

        5. **Tools & Systems Training**
           For each tool in [{', '.join(request.tools)}]:
           - Training sessions or tutorials
           - Practice exercises
           - Access and permissions needed
           - Key workflows to master

        6. **{request.arrangement} Work Considerations**
           - Specific guidance for {request.arrangement} work setup
           - Communication protocols and best practices
           - Virtual/in-person meeting cadence
           - Team collaboration approaches

        7. **Success Metrics & Checkpoints**
           - Key performance indicators
           - Regular check-in schedule (weekly, bi-weekly)
           - Feedback mechanisms
           - 30/60/90 day review milestones (adjusted for {request.duration} days)

        8. **Resources & Support**
           - Documentation and knowledge base
           - Learning resources for skills and tools
           - Who to contact for different needs

        {"9. **Company Culture & Values**" if request.include_culture else ""}
        {'''   - Introduction to company mission, vision, and values
           - Cultural norms and communication style
           - Team dynamics and collaboration approaches
           - Company traditions and social events
           - How to embody company values in daily work''' if request.include_culture else ""}

        {"10. **Mentorship Program**" if request.include_mentorship else "9. **Mentorship Program**" if not request.include_culture else ""}
        {'''   - Assigned mentor and buddy system
           - Scheduled 1-on-1 mentor meetings (weekly/bi-weekly)
           - Topics to discuss with mentor
           - How to get the most from mentorship relationship
           - Peer learning opportunities and knowledge sharing''' if request.include_mentorship else ""}

        Make the plan actionable, realistic, and welcoming. Include specific activities and timelines.
        Consider the {request.arrangement} work arrangement in all recommendations.
    """)

    # Generate content using AI service (exceptions will be caught by global handlers)
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    logger.info(
        f"Successfully generated onboarding plan in {generation_time:.2f}s",
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
        title = f"Onboarding Plan: {request.position} - {request.duration} days"
        db_document = GeneratedDocument(
            doc_type=DocumentType.ONBOARDING_PLAN,
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
            f"Saved onboarding plan to database (ID: {db_document.id})",
            extra={"trace_id": trace_id, "document_id": db_document.id}
        )

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2),
        id=document_id
    )
