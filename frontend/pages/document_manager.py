"""Document Management Page - View, export, and manage all generated documents."""

import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_helper import (
    get_all_documents,
    get_document_by_id,
    delete_document,
    show_export_buttons
)

def document_manager_page():
    """Document management interface."""
    st.markdown("""
        <style>
        .stButton button {
            background: linear-gradient(to left, #FF4B2B, #FF416C) !important;
            color: white !important;
            font-weight: 800 !important;
            font-size: 1.4rem !important;
            padding: 0.8rem 1.5rem !important;
            border-radius: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        .document-card {
            background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            border: 2px solid #333;
            transition: all 0.3s ease;
        }
        .document-card:hover {
            transform: translateY(-5px);
            border-color: #EF629F;
            box-shadow: 0 10px 30px rgba(239, 98, 159, 0.3);
        }
        .doc-title {
            color: #EF629F;
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .doc-type {
            background: linear-gradient(to right, #EF629F, #EECDA3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .doc-date {
            color: #888;
            font-size: 0.85rem;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Main Dashboard", type="primary"):
        st.session_state.page = "main"
        st.rerun()

    st.title("📚 Document Manager")
    st.markdown("### View, Export, and Manage All Generated Documents")

    # Filter options
    col1, col2 = st.columns([3, 1])
    with col1:
        doc_type_filter = st.selectbox(
            "Filter by Document Type",
            ["All", "job_description", "offer_letter", "interview_questions", "onboarding_plan"],
            format_func=lambda x: x.replace('_', ' ').title() if x != "All" else "All Documents"
        )

    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")

    # Fetch documents
    with st.spinner("Loading documents..."):
        try:
            filter_param = None if doc_type_filter == "All" else doc_type_filter
            documents = get_all_documents(doc_type=filter_param)

            if not documents:
                st.info("📭 No documents found. Generate some documents to see them here!")
                return

            st.success(f"📄 Found {len(documents)} document(s)")

            # Display documents
            for doc in documents:
                with st.container():
                    st.markdown(f"""
                        <div class="document-card">
                            <div class="doc-title">{doc['title']}</div>
                            <div class="doc-type">Type: {doc['doc_type'].replace('_', ' ').title()}</div>
                            <div class="doc-date">Created: {doc['created_at']}</div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Action buttons
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

                    with col1:
                        if st.button(f"👁️ View", key=f"view_{doc['id']}", use_container_width=True):
                            st.session_state[f"show_content_{doc['id']}"] = not st.session_state.get(f"show_content_{doc['id']}", False)
                            st.rerun()

                    with col2:
                        # Export DOCX
                        docx_url = f"http://localhost:8000/api/v1/export/docx/{doc['id']}"
                        st.markdown(
                            f'<a href="{docx_url}" target="_blank"><button style="width:100%; padding:0.5rem; background:#4CAF50; color:white; border:none; border-radius:5px; cursor:pointer;">📄 DOCX</button></a>',
                            unsafe_allow_html=True
                        )

                    with col3:
                        # Export PDF
                        pdf_url = f"http://localhost:8000/api/v1/export/pdf/{doc['id']}"
                        st.markdown(
                            f'<a href="{pdf_url}" target="_blank"><button style="width:100%; padding:0.5rem; background:#2196F3; color:white; border:none; border-radius:5px; cursor:pointer;">📑 PDF</button></a>',
                            unsafe_allow_html=True
                        )

                    with col4:
                        if st.button(f"🗑️", key=f"delete_{doc['id']}", use_container_width=True, help="Delete document"):
                            if delete_document(doc['id']):
                                st.success(f"Deleted: {doc['title']}")
                                st.rerun()

                    # Show content if expanded
                    if st.session_state.get(f"show_content_{doc['id']}", False):
                        st.markdown("#### Document Content")
                        doc_details = get_document_by_id(doc['id'])
                        if doc_details:
                            st.markdown(doc_details['content'])
                            st.markdown("---")

        except Exception as e:
            st.error(f"Error loading documents: {str(e)}")

if __name__ == "__main__":
    document_manager_page()
