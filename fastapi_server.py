from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Callable
from dotenv import load_dotenv
import os
import logging
from langchain_openai import AzureChatOpenAI
import groq
import textwrap
from functools import lru_cache

app = FastAPI(
    title="ByticalGPT API",
    version="1.0.0",
    description="AI-powered HR Assistant API for generating various HR documents"
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class Settings:
    AZURE_API_KEY: str = os.getenv("AZURE_API_KEY")
    AZURE_API_VERSION: str = os.getenv("AZURE_API_VERSION")
    AZURE_API_ENDPOINT: str = os.getenv("AZURE_API_ENDPOINT")
    AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME")
    AZURE_TEMPERATURE: float = float(os.getenv("AZURE_TEMPERATURE", "0.7"))
    AZURE_MAX_TOKENS: int = int(os.getenv("AZURE_MAX_TOKENS", "2000"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL")
    GROQ_TEMPERATURE: float = float(os.getenv("GROQ_TEMPERATURE", "0.7"))
    GROQ_MAX_TOKENS: int = int(os.getenv("GROQ_MAX_TOKENS", "2000"))

@lru_cache()
def get_settings():
    return Settings()

class BaseRequest(BaseModel):
    model_choice: str = Field(default='bytical_mini', description="AI model choice: 'bytical_mini' or 'bytical_versatile'")

class GenerateJDRequest(BaseRequest):
    job_title: str = Field(..., min_length=2, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    exp_level: int = Field(..., ge=0, le=50)
    qualification: str = Field(..., min_length=2)
    req_skills: List[str] = Field(..., min_items=1)
    role: str = Field(..., min_length=10)
    salary: str
    location: str

class GenerateInterviewRequest(BaseRequest):
    role: str = Field(..., min_length=2)
    focus_area: str = Field(..., min_length=2)
    experience_level: int = Field(..., ge=0, le=50)
    technical_skills: List[str] = Field(..., min_items=1)
    soft_skills: List[str] = Field(..., min_items=1)

class GenerateOfferRequest(BaseRequest):
    name: str = Field(..., min_length=2)
    position: str = Field(..., min_length=2)
    department: str = Field(..., min_length=2)
    salary: str = Field(..., min_length=2)
    start_date: str = Field(..., min_length=2)
    location: str = Field(..., min_length=2)

class GenerateOnboardingRequest(BaseRequest):
    position: str = Field(..., min_length=2)
    department: str = Field(..., min_length=2)
    duration: int = Field(..., ge=1)
    arrangement: str = Field(..., min_length=2)
    skills: List[str] = Field(..., min_items=1)
    tools: List[str] = Field(..., min_items=1)

class GenerateReviewRequest(BaseRequest):
    employee_name: str = Field(..., min_length=2)
    position: str = Field(..., min_length=2)
    review_period: str = Field(..., min_length=2)
    achievements: List[str] = Field(..., min_items=1)
    skills: List[str] = Field(..., min_items=1)
    goals: List[str] = Field(..., min_items=1)
    rating: float = Field(..., ge=0, le=10)

class AIGenerationService:
    def __init__(self, settings: Settings = Depends(get_settings)):
        self.settings = settings

    def generate_with_azure(self, prompt: str) -> str:
        if not self.settings.AZURE_API_KEY:
            raise ValueError("AZURE_API_KEY is not set")
        
        llm = AzureChatOpenAI(
            api_key=self.settings.AZURE_API_KEY,
            api_version=self.settings.AZURE_API_VERSION,
            azure_endpoint=self.settings.AZURE_API_ENDPOINT,
            deployment_name=self.settings.AZURE_DEPLOYMENT_NAME,
            temperature=self.settings.AZURE_TEMPERATURE,
            max_tokens=self.settings.AZURE_MAX_TOKENS
        )
        return llm.invoke(prompt).content

    def generate_with_groq(self, prompt: str) -> str:
        if not self.settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set")
        
        client = groq.Client(api_key=self.settings.GROQ_API_KEY)
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.settings.GROQ_MODEL,
            temperature=self.settings.GROQ_TEMPERATURE,
            max_tokens=self.settings.GROQ_MAX_TOKENS
        )
        return completion.choices[0].message.content

    def get_generator(self, model_choice: str) -> Callable:
        return self.generate_with_azure if model_choice == 'bytical_mini' else self.generate_with_groq

@app.post("/generate_jd")
async def generate_jd(request: GenerateJDRequest, ai_service: AIGenerationService = Depends()):
    logger.info(f"Generating job description for {request.job_title}")
    try:
        prompt = textwrap.dedent(f"""
            Create a professional job description for:
            Job Title: {request.job_title}
            Department: {request.department}
            Experience: {request.exp_level} years
            Qualification: {request.qualification}
            Skills: {', '.join(request.req_skills)}
            Responsibilities: {request.role}
            Salary: {request.salary}
            Location: {request.location}
        """)
        generator = ai_service.get_generator(request.model_choice)
        content = generator(prompt)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error generating job description: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_interview")
async def generate_interview(request: GenerateInterviewRequest, ai_service: AIGenerationService = Depends()):
    logger.info(f"Generating interview questions for {request.role}")
    try:
        prompt = textwrap.dedent(f"""
            Generate comprehensive interview questions for:
            Role: {request.role}
            Focus Area: {request.focus_area}
            Experience Level: {request.experience_level} years
            Technical Skills: {', '.join(request.technical_skills)}
            Soft Skills: {', '.join(request.soft_skills)}
            Include technical, behavioral, and scenario-based questions with evaluation criteria.
        """)
        generator = ai_service.get_generator(request.model_choice)
        content = generator(prompt)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error generating interview questions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_offer")
async def generate_offer(request: GenerateOfferRequest, ai_service: AIGenerationService = Depends()):
    logger.info(f"Generating offer letter for {request.name}")
    try:
        prompt = textwrap.dedent(f"""
            Generate a professional offer letter for:
            Candidate Name: {request.name}
            Position: {request.position}
            Department: {request.department}
            Salary: {request.salary}
            Start Date: {request.start_date}
            Location: {request.location}
            Include company introduction, role details, compensation, and terms.
        """)
        generator = ai_service.get_generator(request.model_choice)
        content = generator(prompt)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error generating offer letter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_onboarding")
async def generate_onboarding(request: GenerateOnboardingRequest, ai_service: AIGenerationService = Depends()):
    logger.info(f"Generating onboarding plan for {request.position}")
    try:
        prompt = textwrap.dedent(f"""
            Create a detailed onboarding plan for:
            Position: {request.position}
            Department: {request.department}
            Duration: {request.duration} days
            Work Type: {request.arrangement}
            Skills Required: {', '.join(request.skills)}
            Tools: {', '.join(request.tools)}
            Include pre-boarding, weekly breakdown, objectives, and success metrics.
        """)
        generator = ai_service.get_generator(request.model_choice)
        content = generator(prompt)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error generating onboarding plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_review")
async def generate_review(request: GenerateReviewRequest, ai_service: AIGenerationService = Depends()):
    logger.info(f"Generating performance review for {request.employee_name}")
    try:
        prompt = textwrap.dedent(f"""
            Generate a comprehensive performance review for:
            Employee: {request.employee_name}
            Position: {request.position}
            Period: {request.review_period}
            Achievements: {', '.join(request.achievements)}
            Skills: {', '.join(request.skills)}
            Goals: {', '.join(request.goals)}
            Rating: {request.rating}/10
            Include performance analysis, achievements, areas for improvement, and development plan.
        """)
        generator = ai_service.get_generator(request.model_choice)
        content = generator(prompt)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error generating performance review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )
