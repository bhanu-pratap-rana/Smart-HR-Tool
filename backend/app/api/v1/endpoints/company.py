"""Company Profile CRUD endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from backend.app.database import get_session
from backend.app.models.database import (
    CompanyProfile,
    CompanyProfileCreate,
    CompanyProfileUpdate,
    CompanyProfileRead
)
from backend.app.core.exceptions import ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/company-profile",
    tags=["Company Profile"]
)


@router.post(
    "",
    response_model=CompanyProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Company Profile",
    description="Create a new company profile. Only one profile can exist at a time."
)
async def create_company_profile(
    profile: CompanyProfileCreate,
    session: Session = Depends(get_session)
) -> CompanyProfileRead:
    """
    Create a new company profile.

    **Note:** This endpoint enforces a single profile constraint.
    If a profile already exists, returns 409 Conflict.

    Args:
        profile: Company profile data
        session: Database session (injected)

    Returns:
        CompanyProfileRead: Created company profile

    Raises:
        ValidationError: If a profile already exists
    """
    # Check if profile already exists
    existing = session.exec(select(CompanyProfile)).first()
    if existing:
        raise ValidationError(
            "Company profile already exists. Use PUT to update or DELETE first."
        )

    # Create new profile
    db_profile = CompanyProfile.model_validate(profile)
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)

    logger.info(f"Created company profile: {db_profile.name} (ID: {db_profile.id})")
    return db_profile


@router.get(
    "",
    response_model=CompanyProfileRead,
    summary="Get Company Profile",
    description="Retrieve the company profile if it exists"
)
async def get_company_profile(
    session: Session = Depends(get_session)
) -> CompanyProfileRead:
    """
    Get the company profile.

    Returns:
        CompanyProfileRead: Company profile data

    Raises:
        ResourceNotFoundError: If no profile exists (404)
    """
    profile = session.exec(select(CompanyProfile)).first()
    if not profile:
        raise ResourceNotFoundError("CompanyProfile", "default")

    return profile


@router.put(
    "",
    response_model=CompanyProfileRead,
    summary="Update Company Profile",
    description="Update the existing company profile"
)
async def update_company_profile(
    profile_update: CompanyProfileUpdate,
    session: Session = Depends(get_session)
) -> CompanyProfileRead:
    """
    Update the company profile.

    Only provided fields will be updated (partial update supported).

    Args:
        profile_update: Fields to update
        session: Database session (injected)

    Returns:
        CompanyProfileRead: Updated company profile

    Raises:
        ResourceNotFoundError: If no profile exists (404)
    """
    profile = session.exec(select(CompanyProfile)).first()
    if not profile:
        raise ResourceNotFoundError("CompanyProfile", "default")

    # Update only provided fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)

    logger.info(f"Updated company profile: {profile.name} (ID: {profile.id})")
    return profile


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Company Profile",
    description="Delete the company profile"
)
async def delete_company_profile(
    session: Session = Depends(get_session)
) -> None:
    """
    Delete the company profile.

    Args:
        session: Database session (injected)

    Raises:
        ResourceNotFoundError: If no profile exists (404)
    """
    profile = session.exec(select(CompanyProfile)).first()
    if not profile:
        raise ResourceNotFoundError("CompanyProfile", "default")

    session.delete(profile)
    session.commit()

    logger.info(f"Deleted company profile: {profile.name} (ID: {profile.id})")
