import streamlit as st
import requests
from datetime import datetime
import io
import markdown
from xhtml2pdf import pisa

def convert_to_pdf(markdown_text):
    html = markdown.markdown(markdown_text)
    
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
            <h1 class="title">Interview Questions</h1>
        </div>
        <div class="content">
            {html}
        </div>
    </body>
    </html>
    """
    
    result = io.BytesIO()
    pdf = pisa.CreatePDF(pdf_html, dest=result)
    return result.getvalue() if not pdf.err else None

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
        </style>
    """, unsafe_allow_html=True)

    if st.button("← Back to Main Dashboard", type="primary"):
        st.session_state.page = "main"
        st.rerun()

    st.title("🚀 Interview Questions Generator")
    st.markdown("### Design targeted interview questions tailored to the role.")

    with st.form("interview_questions_form"):
        col1, col2 = st.columns(2)

        with col1:
            role = st.text_input("Role *", placeholder="e.g., Full Stack Developer")
            focus_area = st.text_input("Focus Area *", placeholder="e.g., System Architecture")
            experience_level = st.number_input("Experience Level (years)", min_value=0, max_value=30, value=3)

        with col2:
            technical_skills = st.text_area("Technical Skills * (Comma separated)", placeholder="e.g., Python, Java, AWS")
            soft_skills = st.text_area("Soft Skills (Comma separated)", placeholder="e.g., Communication, Leadership")

        model_choice = st.session_state.get("model_choice", "default_model")
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
                    "http://localhost:8000/generate_interview",
                    json=payload
                )
                
                if response.status_code == 200:
                    questions = response.json()["content"]
                    st.success("Questions generated successfully!")

                    st.markdown("### Edit Generated Questions")
                    edited_content = st.text_area(
                        "",
                        value=questions,
                        height=400,
                        key="editor_questions"
                    )

                    st.markdown("### Preview")
                    st.markdown(edited_content)

                    pdf_content = convert_to_pdf(edited_content)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download Interview Questions PDF",
                            data=pdf_content,
                            file_name=f"interview_questions_{role.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                else:
                    st.error("Failed to generate questions. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating the questions.")

if __name__ == "__main__":
    interview_questions_page()
