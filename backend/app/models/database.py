"""Database models for Smart HR Tool.

SQLModel is used for ORM, combining SQLAlchemy and Pydantic.
These models define the database schema and API serialization.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, String, Text
from enum import Enum


class DocumentType(str, Enum):
    """Enumeration of supported document types."""

    JOB_DESCRIPTION = "job_description"
    OFFER_LETTER = "offer_letter"
    INTERVIEW_QUESTIONS = "interview_questions"
    ONBOARDING_PLAN = "onboarding_plan"
    PERFORMANCE_REVIEW = "performance_review"


# ============================================================================
# Company Profile Models
# ============================================================================

class CompanyProfileBase(SQLModel):
    """Base model for CompanyProfile with shared fields."""

    name: str = Field(max_length=200, description="Company name")
    industry: Optional[str] = Field(default=None, max_length=100, description="Industry sector")
    size: Optional[str] = Field(default=None, max_length=50, description="Company size (e.g., '50-200 employees')")
    location: Optional[str] = Field(default=None, max_length=200, description="Company location")
    website: Optional[str] = Field(default=None, max_length=500, description="Company website URL")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="Company description")
    values: Optional[str] = Field(default=None, sa_column=Column(Text), description="Company values and culture")
    logo_url: Optional[str] = Field(default=None, max_length=500, description="Company logo URL")


class CompanyProfile(CompanyProfileBase, table=True):
    """
    Company profile database model.

    Stores company information used to personalize generated documents.
    Each company has a unique profile that can be referenced by documents.
    """

    __tablename__ = "company_profile"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Relationships
    documents: List["GeneratedDocument"] = Relationship(back_populates="company")


class CompanyProfileCreate(CompanyProfileBase):
    """Schema for creating a new company profile."""
    pass


class CompanyProfileUpdate(SQLModel):
    """Schema for updating an existing company profile. All fields optional."""

    name: Optional[str] = Field(default=None, max_length=200)
    industry: Optional[str] = Field(default=None, max_length=100)
    size: Optional[str] = Field(default=None, max_length=50)
    location: Optional[str] = Field(default=None, max_length=200)
    website: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None)
    values: Optional[str] = Field(default=None)
    logo_url: Optional[str] = Field(default=None, max_length=500)


class CompanyProfileRead(CompanyProfileBase):
    """Schema for reading company profile (includes ID and timestamps)."""

    id: int
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Generated Document Models
# ============================================================================

class GeneratedDocumentBase(SQLModel):
    """Base model for GeneratedDocument with shared fields."""

    doc_type: DocumentType = Field(description="Type of document")
    title: str = Field(max_length=300, description="Document title")
    content: str = Field(sa_column=Column(Text), description="Generated content (markdown)")
    model_used: str = Field(max_length=100, description="AI model used for generation")
    generation_time: Optional[float] = Field(default=None, description="Generation time in seconds")

    # Optional company association
    company_id: Optional[int] = Field(default=None, foreign_key="company_profile.id", description="Associated company profile")


class GeneratedDocument(GeneratedDocumentBase, table=True):
    """
    Generated document database model.

    Stores all AI-generated HR documents with full content, metadata,
    and optional association to a company profile.
    """

    __tablename__ = "generated_document"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    # Relationships
    company: Optional[CompanyProfile] = Relationship(back_populates="documents")


class GeneratedDocumentCreate(GeneratedDocumentBase):
    """Schema for creating a new generated document."""
    pass


class GeneratedDocumentUpdate(SQLModel):
    """Schema for updating an existing document. All fields optional."""

    title: Optional[str] = Field(default=None, max_length=300)
    content: Optional[str] = Field(default=None)


class GeneratedDocumentRead(GeneratedDocumentBase):
    """Schema for reading generated document (includes ID and timestamps)."""

    id: int
    created_at: datetime
    updated_at: datetime


# ============================================================================
# Export All Models
# ============================================================================

__all__ = [
    "DocumentType",
    "CompanyProfile",
    "CompanyProfileCreate",
    "CompanyProfileUpdate",
    "CompanyProfileRead",
    "GeneratedDocument",
    "GeneratedDocumentCreate",
    "GeneratedDocumentUpdate",
    "GeneratedDocumentRead",
]
