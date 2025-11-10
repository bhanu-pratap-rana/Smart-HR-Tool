"""
Shared utility module for document export functionality.
Provides helper functions to export documents via backend API.
"""

import streamlit as st
import requests
from typing import Optional, Dict, Any
from datetime import datetime

API_BASE_URL = "http://localhost:8000"


def export_document_docx(document_id: int, filename: str) -> Optional[bytes]:
    """
    Export document as DOCX via backend API.

    Args:
        document_id: ID of the document to export
        filename: Filename for download button

    Returns:
        bytes: DOCX file content, or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/export/docx/{document_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Failed to export DOCX: {response.status_code}")
            return None

    except requests.RequestException as e:
        st.error(f"Export error: {str(e)}")
        return None


def export_document_pdf(document_id: int, filename: str) -> Optional[bytes]:
    """
    Export document as PDF via backend API.

    Args:
        document_id: ID of the document to export
        filename: Filename for download button

    Returns:
        bytes: PDF file content, or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/export/pdf/{document_id}",
            timeout=30
        )

        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Failed to export PDF: {response.status_code}")
            return None

    except requests.RequestException as e:
        st.error(f"Export error: {str(e)}")
        return None


def show_export_buttons(document_id: int, doc_title: str):
    """
    Display DOCX and PDF export buttons for a document.

    Args:
        document_id: ID of the document to export
        doc_title: Title of document (used for filename)
    """
    # Sanitize filename
    safe_filename = doc_title.lower().replace(' ', '_').replace('/', '_')

    col1, col2 = st.columns(2)

    with col1:
        docx_bytes = export_document_docx(document_id, f"{safe_filename}.docx")
        if docx_bytes:
            st.download_button(
                label="📄 Download DOCX",
                data=docx_bytes,
                file_name=f"{safe_filename}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key=f"docx_{document_id}",
                use_container_width=True
            )

    with col2:
        pdf_bytes = export_document_pdf(document_id, f"{safe_filename}.pdf")
        if pdf_bytes:
            st.download_button(
                label="📑 Download PDF",
                data=pdf_bytes,
                file_name=f"{safe_filename}.pdf",
                mime="application/pdf",
                key=f"pdf_{document_id}",
                use_container_width=True
            )


def get_all_documents(doc_type: Optional[str] = None) -> list:
    """
    Fetch all documents from backend API.

    Args:
        doc_type: Optional document type filter

    Returns:
        list: List of documents
    """
    try:
        url = f"{API_BASE_URL}/api/v1/documents"
        if doc_type:
            url += f"?doc_type={doc_type}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            # Backend returns a list directly, not a wrapper object
            if isinstance(data, list):
                return data
            # Fallback for backwards compatibility if backend returns wrapper
            return data.get('documents', [])
        else:
            st.error(f"Failed to fetch documents: {response.status_code}")
            return []

    except requests.RequestException as e:
        st.error(f"Error fetching documents: {str(e)}")
        return []


def get_document_by_id(document_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetch a specific document by ID.

    Args:
        document_id: ID of the document

    Returns:
        dict: Document data, or None if failed
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/documents/{document_id}",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch document: {response.status_code}")
            return None

    except requests.RequestException as e:
        st.error(f"Error fetching document: {str(e)}")
        return None


def delete_document(document_id: int) -> bool:
    """
    Delete a document.

    Args:
        document_id: ID of the document to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/v1/documents/{document_id}",
            timeout=10
        )

        # Accept both 200 OK and 204 No Content as success
        if response.status_code in [200, 204]:
            return True
        else:
            st.error(f"Failed to delete document: {response.status_code}")
            return False

    except requests.RequestException as e:
        st.error(f"Error deleting document: {str(e)}")
        return False


def create_company_profile(profile_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Create or update company profile.

    Args:
        profile_data: Company profile information

    Returns:
        dict: Created/updated profile, or None if failed
    """
    try:
        # Try to get existing profile first
        response = requests.get(f"{API_BASE_URL}/api/v1/company-profile", timeout=10)

        if response.status_code == 200:
            # Update existing profile
            response = requests.put(
                f"{API_BASE_URL}/api/v1/company-profile",
                json=profile_data,
                timeout=10
            )
        else:
            # Create new profile
            response = requests.post(
                f"{API_BASE_URL}/api/v1/company-profile",
                json=profile_data,
                timeout=10
            )

        if response.status_code in [200, 201]:
            return response.json()
        else:
            st.error(f"Failed to save company profile: {response.status_code}")
            return None

    except requests.RequestException as e:
        st.error(f"Error saving company profile: {str(e)}")
        return None


def get_company_profile() -> Optional[Dict[str, Any]]:
    """
    Fetch company profile.

    Returns:
        dict: Company profile data, or None if not found
    """
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/company-profile",
            timeout=10
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except requests.RequestException as e:
        return None


__all__ = [
    'export_document_docx',
    'export_document_pdf',
    'show_export_buttons',
    'get_all_documents',
    'get_document_by_id',
    'delete_document',
    'create_company_profile',
    'get_company_profile'
]
