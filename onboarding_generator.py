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
            <h1 class="title">Onboarding Plan</h1>
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

    st.title("🚀 Onboarding Plan Generator")
    st.markdown("### Create Comprehensive Onboarding Plans")

    with st.form("onboarding_plan_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            position = st.text_input("Position Title *", placeholder="e.g., Senior Software Engineer")
            department = st.text_input("Department *", placeholder="e.g., Engineering")
            arrangement = st.selectbox("Work Arrangement *", ["On-site", "Remote", "Hybrid"])
            duration = st.number_input("Onboarding Duration (days)", min_value=7, max_value=180, value=30)
        
        with col2:
            skills = st.text_area("Required Skills * (Comma separated)", placeholder="e.g., Python, Java, AWS")
            tools = st.text_area("Tools & Software (Comma separated)", placeholder="e.g., JIRA, Git, VS Code")
        
        responsibilities = st.text_area("Key Responsibilities *", placeholder="Describe main duties and responsibilities")
        
        with st.expander("Additional Options"):
            include_compliance = st.checkbox("Include Compliance Training", value=True)
            include_culture = st.checkbox("Include Culture Sessions", value=True)
            include_mentorship = st.checkbox("Include Mentorship Program", value=True)
        
        model_choice = st.session_state.get("model_choice", "default_model")
        submit_button = st.form_submit_button("Generate Onboarding Plan", type="primary")

    if submit_button:
        if not all([position, department, skills, responsibilities]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("Generating onboarding plan..."):
            try:
                skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
                tools_list = [tool.strip() for tool in tools.split(',')] if tools else []

                payload = {
                    "position": position,
                    "department": department,
                    "arrangement": arrangement,
                    "duration": duration,
                    "skills": skills_list,
                    "tools": tools_list,
                    "responsibilities": responsibilities,
                    "include_compliance": include_compliance,
                    "include_culture": include_culture,
                    "include_mentorship": include_mentorship,
                    "model_choice": model_choice
                }

                response = requests.post(
                    "http://localhost:8000/generate_onboarding",
                    json=payload
                )
                
                if response.status_code == 200:
                    onboarding_content = response.json()["content"]
                    st.success("Onboarding plan generated successfully!")

                    st.markdown("### Edit Generated Content")
                    edited_content = st.text_area(
                        "",
                        value=onboarding_content,
                        height=400,
                        key="editor_onboarding"
                    )

                    st.markdown("### Preview")
                    st.markdown(edited_content)

                    pdf_content = convert_to_pdf(edited_content)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download Onboarding Plan PDF",
                            data=pdf_content,
                            file_name=f"onboarding_plan_{position.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                else:
                    st.error("Failed to generate onboarding plan. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating the onboarding plan.")

if __name__ == "__main__":
    onboarding_plan_page()
