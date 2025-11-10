import streamlit as st
import requests
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.export_helper import show_export_buttons

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
                    "http://localhost:8000/api/v1/offer-letter/generate?save_to_db=true",
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    result_data = response.json()
                    offer_content = result_data["content"]
                    document_id = result_data.get("id")

                    st.success("✅ Offer Letter generated and saved to database successfully!")

                    st.markdown("### Generated Offer Letter")
                    st.markdown(offer_content)

                    # Show export buttons if document was saved to database
                    if document_id:
                        st.markdown("### Export Document")
                        st.info("📥 Download your offer letter in professional formats with company branding")
                        show_export_buttons(document_id, f"offer_letter_{name}")
                    else:
                        st.warning("Document was not saved to database. Export functionality unavailable.")

                else:
                    error_msg = response.json().get('detail', 'Unknown error') if response.status_code != 500 else 'Server error'
                    st.error(f"Failed to generate offer letter: {error_msg}")

            except Exception as e:
                st.error("An error occurred while generating the offer letter.")

if __name__ == "__main__":
    offer_letter_page()
