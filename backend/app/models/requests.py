"""Request models for API endpoints."""

from typing import List
from pydantic import BaseModel, Field, ConfigDict


class BaseRequest(BaseModel):
    """Base request model with common fields."""

    model_choice: str = Field(
        default="hrcraft_mini",
        description="AI model choice: 'hrcraft_mini' (Ollama) or 'hrcraft_pro' (Groq)"
    )

    # Fix for Pydantic warning about 'model_' namespace
    model_config = ConfigDict(
        protected_namespaces=(),  # Disable protected namespace warning
        str_strip_whitespace=True,
        validate_assignment=True
    )


class GenerateJDRequest(BaseRequest):
    """Request model for job description generation."""

    job_title: str = Field(..., min_length=2, max_length=100, description="Job title")
    department: str = Field(..., min_length=2, max_length=100, description="Department name")
    exp_level: int = Field(..., ge=0, le=50, description="Years of experience required")
    qualification: str = Field(..., min_length=2, description="Required qualifications")
    req_skills: List[str] = Field(..., min_items=1, description="Required skills")
    role: str = Field(..., min_length=2, description="Role description and responsibilities")
    salary: str = Field(..., description="Salary range")
    location: str = Field(..., description="Job location")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "job_title": "Senior Python Developer",
                "department": "Engineering",
                "exp_level": 5,
                "qualification": "Bachelor's degree in Computer Science",
                "req_skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                "role": "Develop and maintain backend services using Python and FastAPI",
                "salary": "$100,000 - $150,000",
                "location": "Remote",
                "model_choice": "hrcraft_mini"
            }
        }
    )


class GenerateInterviewRequest(BaseRequest):
    """Request model for interview questions generation."""

    role: str = Field(..., min_length=2, description="Job role")
    focus_area: str = Field(..., min_length=2, description="Interview focus area")
    experience_level: int = Field(..., ge=0, le=50, description="Years of experience")
    technical_skills: List[str] = Field(..., min_items=1, description="Technical skills to assess")
    soft_skills: List[str] = Field(..., min_items=1, description="Soft skills to assess")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "role": "Full Stack Developer",
                "focus_area": "Backend Development",
                "experience_level": 3,
                "technical_skills": ["Python", "JavaScript", "SQL"],
                "soft_skills": ["Communication", "Teamwork", "Problem Solving"],
                "model_choice": "hrcraft_pro"
            }
        }
    )


class GenerateOfferRequest(BaseRequest):
    """Request model for offer letter generation."""

    name: str = Field(..., min_length=2, description="Candidate name")
    position: str = Field(..., min_length=2, description="Job position")
    department: str = Field(..., min_length=2, description="Department")
    salary: str = Field(..., min_length=2, description="Salary details")
    start_date: str = Field(..., min_length=2, description="Start date")
    location: str = Field(..., min_length=2, description="Work location")
    reporting_to: str = Field(default="", description="Reporting manager name")
    benefits: str = Field(default="", description="Additional benefits and perks")
    special_terms: str = Field(default="", description="Special terms and conditions")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "position": "Software Engineer",
                "department": "Engineering",
                "salary": "$120,000 per year",
                "start_date": "January 15, 2025",
                "location": "San Francisco, CA",
                "reporting_to": "Jane Smith, Engineering Manager",
                "benefits": "Health insurance, 401k matching, gym membership",
                "special_terms": "Remote work allowed, flexible hours",
                "model_choice": "hrcraft_mini"
            }
        }
    )


class GenerateOnboardingRequest(BaseRequest):
    """Request model for onboarding plan generation."""

    position: str = Field(..., min_length=2, description="Job position")
    department: str = Field(..., min_length=2, description="Department")
    duration: int = Field(..., ge=1, description="Onboarding duration in days")
    arrangement: str = Field(..., min_length=2, description="Work arrangement (remote/hybrid/onsite)")
    skills: List[str] = Field(..., min_items=1, description="Skills to develop")
    tools: List[str] = Field(..., min_items=1, description="Tools and systems to learn")
    include_culture: bool = Field(default=True, description="Include company culture section")
    include_mentorship: bool = Field(default=True, description="Include mentorship program section")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "position": "Frontend Developer",
                "department": "Engineering",
                "duration": 30,
                "arrangement": "Hybrid",
                "skills": ["React", "TypeScript", "CSS"],
                "tools": ["GitHub", "Jira", "Figma"],
                "include_culture": True,
                "include_mentorship": True,
                "model_choice": "hrcraft_pro"
            }
        }
    )


class GenerateReviewRequest(BaseRequest):
    """Request model for performance review generation."""

    employee_name: str = Field(..., min_length=2, description="Employee name")
    position: str = Field(..., min_length=2, description="Job position")
    review_period: str = Field(..., min_length=2, description="Review period")
    achievements: List[str] = Field(..., min_items=1, description="Key achievements")
    skills: List[str] = Field(..., min_items=1, description="Skills demonstrated")
    goals: List[str] = Field(..., min_items=1, description="Goals for next period")
    rating: float = Field(..., ge=0, le=10, description="Overall performance rating (0-10)")

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "employee_name": "Jane Smith",
                "position": "Senior Developer",
                "review_period": "Q4 2024",
                "achievements": [
                    "Led migration to microservices",
                    "Mentored 3 junior developers",
                    "Reduced API response time by 40%"
                ],
                "skills": ["Leadership", "Architecture", "Performance Optimization"],
                "goals": [
                    "Complete AWS certification",
                    "Lead new project initiative",
                    "Improve code review process"
                ],
                "rating": 8.5,
                "model_choice": "hrcraft_mini"
            }
        }
    )
