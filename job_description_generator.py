import streamlit as st
import requests
from datetime import datetime
import io
import markdown
from xhtml2pdf import pisa
import binascii  # Updated import
import os
import ntpath  # Added import

def convert_to_pdf(markdown_text):
    html_content = markdown.markdown(markdown_text, extensions=['fenced_code', 'tables'])

    styles = """
    @page {
        size: A4;
        margin: 2.5cm;
    }
    body {
        font-family: Arial, sans-serif;
        color: #333333;
        line-height: 1.6;
        font-size: 12pt;
    }
    .header {
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #333333;
        padding-bottom: 15px;
    }
    .title {
        font-size: 24pt;
        font-weight: bold;
        margin: 0;
        text-transform: uppercase;
    }
    .content {
        margin-top: 20px;
    }
    .content h1, .content h2, .content h3 {
        color: #333333;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .content h1 { font-size: 18pt; }
    .content h2 { font-size: 16pt; }
    .content h3 { font-size: 14pt; }
    .content p {
        text-align: justify;
        margin-bottom: 10px;
    }
    .content ul, .content ol {
        margin: 10px 0 10px 20px;
        padding-left: 15px;
    }
    .content li {
        margin-bottom: 5px;
        text-align: justify;
    }
    """

    pdf_html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>{styles}</style>
    </head>
    <body>
        <div class="header">
            <h1 class="title">Job Description</h1>
        </div>
        <div class="content">
            {html_content}
        </div>
    </body>
    </html>
    """

    result = io.BytesIO()
    pdf = pisa.CreatePDF(pdf_html, dest=result)
    return result.getvalue() if not pdf.err else None




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
        
        model_choice = st.session_state.get("model_choice", "default_model")
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
                    "http://localhost:8000/generate_jd",
                    json=payload
                )
                
                if response.status_code == 200:
                    jd_content = response.json()["content"]
                    st.success("Job Description generated successfully!")

                    st.markdown("### Edit Generated Content")
                    edited_content = st.text_area(
                        "",
                        value=jd_content,
                        height=400,
                        key="editor_jd"
                    )

                    st.markdown("### Preview")
                    st.markdown(edited_content)

                    pdf_content = convert_to_pdf(edited_content)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download Job Description PDF",
                            data=pdf_content,
                            file_name=f"job_description_{job_title.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                    else:
                        st.error("Failed to generate PDF. Please try again.")
                else:
                    st.error("Failed to generate job description. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating the job description.")

if __name__ == "__main__":
    job_description_page()