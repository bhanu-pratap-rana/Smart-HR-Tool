import streamlit as st
import requests
from datetime import datetime
import io
import markdown
from xhtml2pdf import pisa
import base64
import os

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
            <h1 class="title">Offer Letter</h1>
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

def offer_letter_page():
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

    st.title("📨 Offer Letter Generator")
    st.markdown("### Create Professional Offer Letters")

    with st.form("offer_letter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Candidate Name *", placeholder="e.g., John Doe")
            position = st.text_input("Position *", placeholder="e.g., Senior Software Engineer")
            department = st.text_input("Department *", placeholder="e.g., Engineering")
            start_date = st.date_input("Start Date *")
        
        with col2:
            salary = st.number_input("Annual Salary (LPA) *", min_value=0.0, step=1.0)
            location = st.selectbox("Work Location *", ["On-site", "Hybrid", "Remote", "Flexible"])
            reporting_to = st.text_input("Reporting Manager", placeholder="e.g., Jane Smith")
        
        additional_benefits = st.text_area("Additional Benefits", placeholder="List additional perks and benefits")
        special_terms = st.text_area("Special Terms & Conditions", placeholder="Any special terms or conditions")
        
        model_choice = st.session_state.get("model_choice", "default_model")
        submit_button = st.form_submit_button("Generate Offer Letter", type="primary")

    if submit_button:
        if not all([name, position, department, start_date, salary, location]):
            st.error("Please fill in all required fields marked with *")
            return

        with st.spinner("Generating offer letter..."):
            try:
                payload = {
                    "name": name,
                    "position": position,
                    "department": department,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "salary": f"{salary} LPA",
                    "location": location,
                    "reporting_to": reporting_to,
                    "benefits": additional_benefits,
                    "special_terms": special_terms,
                    "model_choice": model_choice
                }

                response = requests.post(
                    "http://localhost:8000/generate_offer",
                    json=payload
                )
                
                if response.status_code == 200:
                    offer_content = response.json()["content"]
                    st.success("Offer letter generated successfully!")

                    st.markdown("### Edit Generated Content")
                    edited_content = st.text_area(
                        "",
                        value=offer_content,
                        height=400,
                        key="editor_offer"
                    )

                    st.markdown("### Preview")
                    st.markdown(edited_content)

                    pdf_content = convert_to_pdf(edited_content)
                    if pdf_content:
                        st.download_button(
                            label="📑 Download Offer Letter PDF",
                            data=pdf_content,
                            file_name=f"offer_letter_{name.lower().replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                else:
                    st.error("Failed to generate offer letter. Please try again.")

            except Exception as e:
                st.error("An error occurred while generating the offer letter.")

if __name__ == "__main__":
    offer_letter_page()
