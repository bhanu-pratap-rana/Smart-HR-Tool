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
    .signature-section {
        margin-top: 50px;
        display: flex;
        justify-content: space-between;
    }
    .signature {
        width: 200px;
        border-top: 1px solid #333333;
        padding-top: 10px;
        text-align: center;
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
            <h1 class="title">Performance Review</h1>
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

def performance_review_page():
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

    st.title("📊 Performance Review Generator")
    st.markdown("### Generate Comprehensive Performance Reviews")

    with st.form("performance_review_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            employee_name = st.text_input("Employee Name *", placeholder="e.g., John Doe")
            position = st.text_input("Position *", placeholder="e.g., Software Engineer")
            review_period = st.text_input("Review Period *", placeholder="e.g., Jan 2024 - Dec 2024")
        
        with col2:
            rating = st.slider("Performance Rating", 1, 10, 7)
            
        achievements = st.text_area("Key Achievements *", 
                                  placeholder="Enter achievements (one per line)")
        skills = st.text_area("Skills Assessment *", 
                             placeholder="Enter skills (one per line)")
        goals = st.text_area("Future Goals *", 
                            placeholder="Enter goals (one per line)")
        
        model_choice = st.session_state.get("model_choice", "bytical_mini")
        submit_button = st.form_submit_button("Generate Performance Review", type="primary")

    if submit_button:
        if not all([employee_name, position, review_period, achievements, skills, goals]):
            st.error("Please fill in all required fields marked with *")
            return

        achievements_list = [x.strip() for x in achievements.split('\n') if x.strip()]
        skills_list = [x.strip() for x in skills.split('\n') if x.strip()]
        goals_list = [x.strip() for x in goals.split('\n') if x.strip()]

        payload = {
            "model_choice": model_choice,
            "employee_name": employee_name,
            "position": position,
            "review_period": review_period,
            "achievements": achievements_list,
            "skills": skills_list,
            "goals": goals_list,
            "rating": rating
        }

        with st.spinner("Generating performance review..."):
            try:
                response = requests.post(
                    "http://localhost:8000/api/v1/performance-review/generate?save_to_db=true",
                    json=payload
                )
                
                if response.status_code == 200:
                    review_content = response.json()["content"]
                    st.success("Performance review generated successfully!")

                    st.markdown("### Edit Generated Content")
                    edited_content = st.text_area(
                        "",
                        value=review_content,
                        height=400,
                        key="editor_review"
                    )

                    st.markdown("### Preview")
                    st.markdown(edited_content)

                    pdf_content = convert_to_pdf(edited_content)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download Performance Review PDF",
                            data=pdf_content,
                            file_name=f"performance_review_{employee_name.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                else:
                    st.error("Failed to generate performance review. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating the performance review.")

if __name__ == "__main__":
    performance_review_page()
