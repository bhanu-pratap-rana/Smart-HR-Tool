import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_helper import show_export_buttons


def onboarding_plan_page():
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
        </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Main Dashboard", type="primary"):
        st.session_state.page = "main"
        st.rerun()

    st.title("🚀 Onboarding Plan Generator")
    st.markdown("### Design Comprehensive Onboarding Plans")

    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)

        with col1:
            position = st.text_input("Position *", placeholder="e.g., Software Engineer")
            department = st.text_input("Department *", placeholder="e.g., Engineering")
            duration = st.number_input("Duration (days)", min_value=1, max_value=180, value=30)

        with col2:
            arrangement = st.selectbox("Work Arrangement", ["On-site", "Remote", "Hybrid"])
            skills = st.text_area("Key Skills (Comma separated)", placeholder="e.g., Python, Git, Agile")
            tools = st.text_area("Tools & Systems (Comma separated)", placeholder="e.g., JIRA, Slack, GitHub")

        include_culture = st.checkbox("Include Company Culture Section", value=True)
        include_mentorship = st.checkbox("Include Mentorship Program", value=True)

        model_choice = st.session_state.get("model_choice", "hrcraft_mini")
        submit_button = st.form_submit_button("Generate Onboarding Plan", type="primary")

    if submit_button:
        if not all([position, department]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("Generating onboarding plan..."):
            try:
                skills_list = [skill.strip() for skill in skills.split(',')] if skills else []
                tools_list = [tool.strip() for tool in tools.split(',')] if tools else []

                payload = {
                    "position": position,
                    "department": department,
                    "duration": duration,
                    "arrangement": arrangement,
                    "skills": skills_list,
                    "tools": tools_list,
                    "include_culture": include_culture,
                    "include_mentorship": include_mentorship,
                    "model_choice": model_choice
                }

                response = requests.post(
                    "http://localhost:8000/api/v1/onboarding-plan/generate?save_to_db=true",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result_data = response.json()
                    onboarding_content = result_data["content"]
                    document_id = result_data.get("id")

                    st.success("✅ Onboarding Plan generated and saved to database successfully!")

                    st.markdown("### Generated Onboarding Plan")
                    st.markdown(onboarding_content)

                    # Show export buttons if document was saved to database
                    if document_id:
                        st.markdown("### Export Document")
                        st.info("📥 Download your onboarding plan in professional formats with company branding")
                        show_export_buttons(document_id, f"onboarding_plan_{position}")
                    else:
                        st.warning("Document was not saved to database. Export functionality unavailable.")

                else:
                    error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
                    st.error(f"Failed to generate onboarding plan: {error_msg}")

            except Exception as e:
                st.error(f"An error occurred while generating the onboarding plan: {str(e)}")

if __name__ == "__main__":
    onboarding_plan_page()
