import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_helper import show_export_buttons


def interview_questions_page():
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
        .editor-container {
            background: #2a2a2a;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }
        .stTextArea textarea {
            background-color: #2D2D2D !important;
            color: white !important;
            border: 2px solid #FF416C !important;
            border-radius: 10px !important;
            padding: 15px !important;
            font-size: 1.1rem !important;
        }
        .stNumberInput input {
            background-color: #2D2D2D !important;
            color: white !important;
            border: 2px solid #FF416C !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Main Dashboard", type="primary"):
        st.session_state.page = "main"
        st.rerun()

    st.title("❓ Interview Questions Generator")
    st.markdown("### Create Role-Specific Interview Questions")

    with st.form("interview_form"):
        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("Role *", placeholder="e.g., Senior Software Engineer")
            focus_area = st.text_input("Focus Area *", placeholder="e.g., Backend Development")
            experience_level = st.number_input("Experience Level (years)", min_value=0, max_value=50, value=5)

        with col2:
            technical_skills = st.text_area("Technical Skills * (Comma separated)", placeholder="e.g., Python, FastAPI, PostgreSQL")
            soft_skills = st.text_area("Soft Skills (Comma separated)", placeholder="e.g., Leadership, Communication")

        model_choice = st.session_state.get("model_choice", "hrcraft_mini")
        submit_button = st.form_submit_button("Generate Questions", type="primary")

    if submit_button:
        if not all([role, focus_area, technical_skills]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("Generating interview questions..."):
            try:
                tech_skills_list = [skill.strip() for skill in technical_skills.split(',') if skill.strip()]
                soft_skills_list = [skill.strip() for skill in soft_skills.split(',')] if soft_skills else []

                payload = {
                    "role": role,
                    "focus_area": focus_area,
                    "experience_level": experience_level,
                    "technical_skills": tech_skills_list,
                    "soft_skills": soft_skills_list,
                    "model_choice": model_choice
                }

                response = requests.post(
                    "http://localhost:8000/api/v1/interview-questions/generate?save_to_db=true",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result_data = response.json()
                    questions = result_data["content"]
                    document_id = result_data.get("id")

                    st.success("✅ Interview Questions generated and saved to database successfully!")

                    st.markdown("### Generated Interview Questions")
                    st.markdown(questions)

                    # Show export buttons if document was saved to database
                    if document_id:
                        st.markdown("### Export Document")
                        st.info("📥 Download your interview questions in professional formats with company branding")
                        show_export_buttons(document_id, f"interview_questions_{role}")
                    else:
                        st.warning("Document was not saved to database. Export functionality unavailable.")

                else:
                    error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
                    st.error(f"Failed to generate questions: {error_msg}")

            except Exception as e:
                st.error(f"An error occurred while generating the questions: {str(e)}")

if __name__ == "__main__":
    interview_questions_page()
