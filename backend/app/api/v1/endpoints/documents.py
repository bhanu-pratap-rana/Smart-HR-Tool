"""Generated Documents storage and retrieval endpoints."""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session, select, col

from backend.app.database import get_session
from backend.app.models.database import (
    GeneratedDocument,
    GeneratedDocumentCreate,
    GeneratedDocumentUpdate,
    GeneratedDocumentRead,
    DocumentType
)
from backend.app.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post(
    "",
    response_model=GeneratedDocumentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Save Generated Document",
    description="Store an AI-generated document in the database"
)
async def create_document(
    document: GeneratedDocumentCreate,
    session: Session = Depends(get_session)
) -> GeneratedDocumentRead:
    """
    Save a generated document to the database.

    Args:
        document: Document data including content and metadata
        session: Database session (injected)

    Returns:
        GeneratedDocumentRead: Saved document with ID and timestamps
    """
    db_document = GeneratedDocument.model_validate(document)
    session.add(db_document)
    session.commit()
    session.refresh(db_document)

    logger.info(
        f"Saved document: {db_document.title} "
        f"(Type: {db_document.doc_type}, ID: {db_document.id})"
    )
    return db_document


@router.get(
    "",
    response_model=List[GeneratedDocumentRead],
    summary="List Generated Documents",
    description="Retrieve all generated documents with optional filtering"
)
async def list_documents(
    doc_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents to return"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    session: Session = Depends(get_session)
) -> List[GeneratedDocumentRead]:
    """
    List generated documents with optional filters.

    Args:
        doc_type: Optional filter by document type
        company_id: Optional filter by company ID
        limit: Maximum results (default: 100)
        offset: Skip N results (default: 0)
        session: Database session (injected)

    Returns:
        List[GeneratedDocumentRead]: List of documents
    """
    # Build query with optional filters
    statement = select(GeneratedDocument)

    if doc_type:
        statement = statement.where(col(GeneratedDocument.doc_type) == doc_type)

    if company_id is not None:
        statement = statement.where(col(GeneratedDocument.company_id) == company_id)

    # Apply pagination
    statement = statement.offset(offset).limit(limit)

    # Order by most recent first
    statement = statement.order_by(col(GeneratedDocument.created_at).desc())

    documents = session.exec(statement).all()

    logger.info(
        f"Listed {len(documents)} documents "
        f"(type: {doc_type}, company_id: {company_id}, limit: {limit}, offset: {offset})"
    )
    return documents


@router.get(
    "/{document_id}",
    response_model=GeneratedDocumentRead,
    summary="Get Document by ID",
    description="Retrieve a specific generated document"
)
async def get_document(
    document_id: int,
    session: Session = Depends(get_session)
) -> GeneratedDocumentRead:
    """
    Get a specific document by ID.

    Args:
        document_id: Document ID
        session: Database session (injected)

    Returns:
        GeneratedDocumentRead: Document data

    Raises:
        ResourceNotFoundError: If document not found (404)
    """
    document = session.get(GeneratedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("GeneratedDocument", str(document_id))

    return document


@router.put(
    "/{document_id}",
    response_model=GeneratedDocumentRead,
    summary="Update Document",
    description="Update document title or content"
)
async def update_document(
    document_id: int,
    document_update: GeneratedDocumentUpdate,
    session: Session = Depends(get_session)
) -> GeneratedDocumentRead:
    """
    Update a document (title or content).

    Args:
        document_id: Document ID
        document_update: Fields to update
        session: Database session (injected)

    Returns:
        GeneratedDocumentRead: Updated document

    Raises:
        ResourceNotFoundError: If document not found (404)
    """
    document = session.get(GeneratedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("GeneratedDocument", str(document_id))

    # Update only provided fields
    update_data = document_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(document, key, value)

    session.add(document)
    session.commit()
    session.refresh(document)

    logger.info(f"Updated document: {document.title} (ID: {document.id})")
    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Document",
    description="Delete a generated document"
)
async def delete_document(
    document_id: int,
    session: Session = Depends(get_session)
) -> None:
    """
    Delete a document.

    Args:
        document_id: Document ID
        session: Database session (injected)

    Raises:
        ResourceNotFoundError: If document not found (404)
    """
    document = session.get(GeneratedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("GeneratedDocument", str(document_id))

    session.delete(document)
    session.commit()

    logger.info(f"Deleted document: {document.title} (ID: {document.id})")
