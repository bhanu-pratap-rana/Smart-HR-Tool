import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_helper import show_export_buttons




def job_description_page():
    """Creates the job description page in the Streamlit app."""
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
        .stSlider {
            padding: 2rem 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Main Dashboard", type="primary"):
        st.session_state.page = "main"
        st.rerun()

    st.title("📝 Job Description Generator")
    st.markdown("### Create Professional Job Descriptions")

    with st.form("job_description_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title *", placeholder="e.g., Senior Software Engineer")
            department = st.text_input("Department *", placeholder="e.g., Engineering")
            exp_level = st.number_input("Required Experience (years)", min_value=0, max_value=50, value=5)
            location = st.selectbox("Work Location *", ["On-site", "Hybrid", "Remote", "Flexible"])
        
        with col2:
            qualification = st.text_input("Qualification Required *", placeholder="e.g., B.Tech in Computer Science")
            req_skills = st.text_area("Required Skills * (Comma separated)", placeholder="e.g., Python, Java, Cloud platforms")
            salary = st.slider("Salary Range (LPA)", 0, 100, (10, 20), key="salary_range")
        
        role_res = st.text_area("Key Responsibilities *", placeholder="List main duties and responsibilities", height=150)
        
        model_choice = st.session_state.get("model_choice", "hrcraft_mini")
        submit_button = st.form_submit_button("Generate Job Description", type="primary")

    if submit_button:
        if not all([job_title, department, qualification, req_skills, role_res]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("Generating job description..."):
            try:
                skills_list = [skill.strip() for skill in req_skills.split(',') if skill.strip()]

                payload = {
                    "job_title": job_title,
                    "department": department,
                    "exp_level": int(exp_level),
                    "qualification": qualification,
                    "req_skills": skills_list,
                    "role": role_res,
                    "salary": f"{salary[0]}-{salary[1]} LPA",
                    "location": location,
                    "model_choice": model_choice
                }

                response = requests.post(
                    "http://localhost:8000/api/v1/job-description/generate?save_to_db=true",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result_data = response.json()
                    jd_content = result_data["content"]
                    document_id = result_data.get("id")

                    st.success("✅ Job Description generated and saved to database successfully!")

                    st.markdown("### Generated Job Description")
                    st.markdown(jd_content)

                    # Show export buttons if document was saved to database
                    if document_id:
                        st.markdown("### Export Document")
                        st.info("📥 Download your job description in professional formats with company branding")
                        show_export_buttons(document_id, f"job_description_{job_title}")
                    else:
                        st.warning("Document was not saved to database. Export functionality unavailable.")

                else:
                    error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
                    st.error(f"Failed to generate job description: {error_msg}")

            except Exception as e:
                st.error("An error occurred while generating the job description.")

if __name__ == "__main__":
    job_description_page()