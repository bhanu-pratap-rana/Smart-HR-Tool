"""Document export endpoints for DOCX and PDF generation."""

import logging
from typing import Optional
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.responses import Response
from sqlmodel import Session

from backend.app.database import get_session
from backend.app.models.database import GeneratedDocument, CompanyProfile
from backend.app.services.document_renderer import DocumentRenderer
from backend.app.core.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/export",
    tags=["Document Export"]
)


@router.get(
    "/docx/{document_id}",
    response_class=Response,
    summary="Export Document as DOCX",
    description="Export a generated document as a branded DOCX file",
    responses={
        200: {
            "description": "DOCX file generated successfully",
            "content": {
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        404: {
            "description": "Document not found"
        },
        500: {
            "description": "Error generating DOCX"
        }
    }
)
async def export_docx(
    document_id: int,
    session: Session = Depends(get_session)
) -> Response:
    """
    Export a generated document as DOCX with company branding.

    Args:
        document_id: ID of the document to export
        session: Database session

    Returns:
        DOCX file as download
    """
    # Get document
    document = session.get(GeneratedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("GeneratedDocument", document_id)

    # Get company profile if associated
    company_profile = None
    if document.company_id:
        company_profile = session.get(CompanyProfile, document.company_id)

    # Create renderer
    renderer = DocumentRenderer(company_profile=company_profile)

    # Prepare metadata
    metadata = {
        "title": document.title,
        "date": document.created_at.strftime('%Y-%m-%d'),
        "reference": f"DOC-{document.id:05d}"
    }

    try:
        # Render DOCX
        docx_bytes = renderer.render_docx(
            content=document.content,
            doc_type=document.doc_type,
            metadata=metadata
        )

        # Generate filename
        filename = f"{document.title.replace(' ', '_')}.docx"

        logger.info(
            f"Exported document {document_id} as DOCX",
            extra={
                "document_id": document_id,
                "document_type": document.doc_type,
                "export_filename": filename
            }
        )

        return Response(
            content=docx_bytes,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        logger.error(
            f"Error generating DOCX for document {document_id}: {e}",
            extra={"document_id": document_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating DOCX: {str(e)}"
        )


@router.get(
    "/pdf/{document_id}",
    response_class=Response,
    summary="Export Document as PDF",
    description="Export a generated document as a branded PDF file",
    responses={
        200: {
            "description": "PDF file generated successfully",
            "content": {
                "application/pdf": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        404: {
            "description": "Document not found"
        },
        500: {
            "description": "Error generating PDF"
        }
    }
)
async def export_pdf(
    document_id: int,
    session: Session = Depends(get_session)
) -> Response:
    """
    Export a generated document as PDF with company branding.

    Args:
        document_id: ID of the document to export
        session: Database session

    Returns:
        PDF file as download
    """
    # Get document
    document = session.get(GeneratedDocument, document_id)
    if not document:
        raise ResourceNotFoundError("GeneratedDocument", document_id)

    # Get company profile if associated
    company_profile = None
    if document.company_id:
        company_profile = session.get(CompanyProfile, document.company_id)

    # Create renderer
    renderer = DocumentRenderer(company_profile=company_profile)

    # Prepare metadata
    metadata = {
        "title": document.title,
        "date": document.created_at.strftime('%Y-%m-%d'),
        "reference": f"DOC-{document.id:05d}"
    }

    try:
        # Render PDF
        pdf_bytes = renderer.render_pdf(
            content=document.content,
            doc_type=document.doc_type,
            metadata=metadata
        )

        # Generate filename
        filename = f"{document.title.replace(' ', '_')}.pdf"

        logger.info(
            f"Exported document {document_id} as PDF",
            extra={
                "document_id": document_id,
                "document_type": document.doc_type,
                "export_filename": filename
            }
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        logger.error(
            f"Error generating PDF for document {document_id}: {e}",
            extra={"document_id": document_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )
