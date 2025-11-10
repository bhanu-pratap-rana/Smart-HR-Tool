import streamlit as st
import requests
import json
from typing import Dict, Any
import asyncio
import aiohttp
from pages.job_description_generator import job_description_page
from pages.onboarding_generator import onboarding_plan_page
from pages.offer_letter_generator import offer_letter_page
from pages.interview_questions_generator import interview_questions_page
from pages.performance_review_generator import performance_review_page
from pages.document_manager import document_manager_page

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="HRCraft AI | Smart HR Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling with responsive design
st.markdown("""
    <style>
    /* Main Container Styling */
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
    }
    
    /* Enhanced Card Styling with Animations */
    .feature-card {
        background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #333;
        animation: scaleIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        background-size: 200% 200%;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        min-height: 200px;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        background-position: right center;
        box-shadow: 
            0 10px 30px rgba(239, 98, 159, 0.3),
            0 0 50px rgba(238, 205, 163, 0.1);
        border-color: #EF629F;
    }
    
    /* Enhanced Title Styling with Animations */
    .card-title {
        background: linear-gradient(to right, #EF629F, #EECDA3, #EF629F);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 10px;
        animation: gradientShift 3s linear infinite;
        transform-origin: left;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover .card-title {
        transform: scale(1.05);
        letter-spacing: 1px;
    }
    
    /* Enhanced Description Styling */
    .card-description {
        color: #e0e0e0;
        font-size: 0.95rem;
        line-height: 1.5;
        font-weight: 400;
        position: relative;
        overflow: hidden;
    }
    
    .card-description::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(to right, transparent, #EF629F, transparent);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover .card-description::after {
        transform: scaleX(1);
    }
    
    /* Enhanced Emoji Icon Animation */
    .emoji-icon {
        font-size: 2rem;
        margin-bottom: 10px;
        animation: float 3s ease-in-out infinite;
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover .emoji-icon {
        transform: scale(1.2) rotate(5deg);
    }
    
    /* Enhanced Button Styling */
    .stButton button {
        background: linear-gradient(to left, #FF4B2B, #FF416C) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 1.4rem !important;
        padding: 0.8rem 1.5rem !important;
        border-radius: 10px !important;
        border: none !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        animation: buttonPulse 2s infinite;
    }
    
    .stButton button:hover {
        background: linear-gradient(to right, #FF4B2B, #FF416C) !important;
        transform: scale(1.05) translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 65, 108, 0.4);
    }
    
    /* Enhanced Heading Animation */
    h1 {
        background: linear-gradient(270deg, #EF629F, #EECDA3, #EF629F);
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 2rem !important;
        animation: gradientShift 3s ease infinite, glowingText 2s ease-in-out infinite;
        padding: 10px;
        border-radius: 15px;
        transform: perspective(1000px) rotateX(0deg);
        transition: transform 0.3s ease;
    }
    
    h1:hover {
        transform: perspective(1000px) rotateX(5deg);
    }
    
    /* Animation Keyframes */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes glowingText {
        0% { text-shadow: 0 0 10px rgba(239, 98, 159, 0.5); }
        50% { text-shadow: 0 0 20px rgba(239, 98, 159, 0.8), 0 0 30px rgba(238, 205, 163, 0.6); }
        100% { text-shadow: 0 0 10px rgba(239, 98, 159, 0.5); }
    }
    
    @keyframes scaleIn {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes buttonPulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255, 65, 108, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 65, 108, 0); }
    }
    
    /* Responsive Design */
    @media screen and (max-width: 768px) {
        .feature-card {
            margin: 10px 5px;
            padding: 15px;
        }
        
        .card-title {
            font-size: 1.4rem;
        }
        
        .card-description {
            font-size: 1rem;
        }
        
        .emoji-icon {
            font-size: 2.5rem;
        }
        
        .stButton button {
            font-size: 1rem !important;
            padding: 0.6rem 1rem !important;
        }
    }
    
    @media screen and (max-width: 480px) {
        .feature-card {
            margin: 8px 2px;
            padding: 12px;
        }
        
        .card-title {
            font-size: 1.2rem;
        }
        
        h1 {
            font-size: 2rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)



# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'model_choice' not in st.session_state:
    st.session_state.model_choice = 'hrcraft_mini'
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# API Integration Functions
# Map old endpoint names to new API v1 paths
ENDPOINT_MAPPING = {
    'generate_jd': 'api/v1/job-description/generate',
    'generate_offer': 'api/v1/offer-letter/generate',
    'generate_interview': 'api/v1/interview-questions/generate',
    'generate_onboarding': 'api/v1/onboarding/generate',
    'generate_review': 'api/v1/performance-review/generate'
}

async def call_api(endpoint: str, data: Dict[Any, Any]) -> Dict[str, str]:
    endpoint_data = {
        'generate_jd': {
            'job_title': st.session_state.form_data.get('job_title', ''),
            'department': st.session_state.form_data.get('department', ''),
            'exp_level': st.session_state.form_data.get('exp_level', 0),
            'qualification': st.session_state.form_data.get('qualification', ''),
            'req_skills': st.session_state.form_data.get('req_skills', []),
            'role': st.session_state.form_data.get('role', ''),
            'salary': st.session_state.form_data.get('salary', ''),
            'location': st.session_state.form_data.get('location', ''),
            'model_choice': data['model_choice']
        },
        'generate_offer': {
            'name': st.session_state.form_data.get('name', ''),
            'position': st.session_state.form_data.get('position', ''),
            'department': st.session_state.form_data.get('department', ''),
            'salary': st.session_state.form_data.get('salary', ''),
            'start_date': st.session_state.form_data.get('start_date', ''),
            'location': st.session_state.form_data.get('location', ''),
            'model_choice': data['model_choice']
        },
        'generate_interview': {
            'role': st.session_state.form_data.get('role', ''),
            'focus_area': st.session_state.form_data.get('focus_area', ''),
            'experience_level': st.session_state.form_data.get('experience_level', 0),
            'technical_skills': st.session_state.form_data.get('technical_skills', []),
            'soft_skills': st.session_state.form_data.get('soft_skills', []),
            'model_choice': data['model_choice']
        },
        'generate_onboarding': {
            'position': st.session_state.form_data.get('position', ''),
            'department': st.session_state.form_data.get('department', ''),
            'duration': st.session_state.form_data.get('duration', 30),
            'arrangement': st.session_state.form_data.get('arrangement', ''),
            'skills': st.session_state.form_data.get('skills', []),
            'tools': st.session_state.form_data.get('tools', []),
            'model_choice': data['model_choice']
        },
        'generate_review': {
            'employee_name': st.session_state.form_data.get('employee_name', ''),
            'position': st.session_state.form_data.get('position', ''),
            'review_period': st.session_state.form_data.get('review_period', ''),
            'achievements': st.session_state.form_data.get('achievements', []),
            'skills': st.session_state.form_data.get('skills', []),
            'goals': st.session_state.form_data.get('goals', []),
            'rating': st.session_state.form_data.get('rating', 0.0),
            'model_choice': data['model_choice']
        }
    }

    request_data = endpoint_data.get(endpoint, {})

    # Get the new API v1 path
    api_path = ENDPOINT_MAPPING.get(endpoint, endpoint)

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_BASE_URL}/{api_path}", json=request_data) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_msg = await response.text()
                raise Exception(f"API Error: {error_msg}")

def show_loading_state():
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 200px;">
            <div class="loading-spinner"></div>
        </div>
    """, unsafe_allow_html=True)

def create_feature_card(title: str, description: str, emoji: str, page: str):
    endpoint_mapping = {
        'jd_generator': 'generate_jd',
        'offer_letter': 'generate_offer',
        'interview_questions': 'generate_interview',
        'onboarding': 'generate_onboarding',
        'performance_review': 'generate_review'
    }

    with st.container():
        st.markdown(f"""
            <div class="feature-card">
                <div class="emoji-icon">{emoji}</div>
                <div class="card-title">{title}</div>
                <div class="card-description">{description}</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Launch {title}", key=f"btn_{page}", use_container_width=True):
            st.session_state.page = page
            endpoint = endpoint_mapping.get(page)
            if endpoint:
                st.session_state.current_endpoint = endpoint
            st.rerun()

def render_form_page():
    if st.session_state.page == 'jd_generator':
        job_description_page()
    elif st.session_state.page == 'offer_letter':
        offer_letter_page()
    elif st.session_state.page == 'interview_questions':
        interview_questions_page()
    elif st.session_state.page == 'onboarding':
        onboarding_plan_page()
    elif st.session_state.page == 'performance_review':
        performance_review_page()
    elif st.session_state.page == 'document_manager':
        document_manager_page()

# Enhanced Sidebar with API Status
with st.sidebar:
    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🤖</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #FF8C42; font-weight: 700;'>HRCraft AI</h2>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #FF8C42; font-weight: 700;'>Settings</h2>", unsafe_allow_html=True)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            st.success("✅ API Connected")
        else:
            st.warning("⚠️ API Connection Issues")
    except:
        st.error("❌ API Not Available")
    
    model_choice = st.selectbox(
        "Select AI Model",
        ["hrcraft_mini", "hrcraft_pro"],
        format_func=lambda x: "HRCraft Mini" if x == "hrcraft_mini" else "HRCraft Pro",
        help="Choose between different AI models for content generation"
    )
    st.session_state.model_choice = model_choice
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #FF8C42; font-weight: 600;'>Model Information</h3>", unsafe_allow_html=True)

    if model_choice == "hrcraft_mini":
        st.info("🚀 HRCraft Mini: Optimized for faster responses")
    else:
        st.info("🌟 HRCraft Pro: Enhanced for complex tasks")
# Main Content with Error Boundary
try:
    st.markdown("<h1 style='text-align: center; font-size: 3rem; margin-bottom: 1rem;'>HRCraft AI - Smart HR Assistant</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: #FF8C42; font-weight: 600;'>Currently using: {st.session_state.model_choice}</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.session_state.page == 'main':
        features = [
            {
                "title": "Job Description Generator",
                "description": "Create professional job descriptions tailored to your needs",
                "emoji": "📝",
                "page": "jd_generator"
            },
            {
                "title": "Offer Letter Generator",
                "description": "Generate personalized offer letters for new hires",
                "emoji": "📨",
                "page": "offer_letter"
            },
            {
                "title": "Interview Question Generator",
                "description": "Create role-specific interview questions",
                "emoji": "❓",
                "page": "interview_questions"
            },
            {
                "title": "Onboarding Plan Generator",
                "description": "Design comprehensive onboarding plans",
                "emoji": "🚀",
                "page": "onboarding"
            },
            {
                "title": "Performance Review Generator",
                "description": "Create detailed performance review templates",
                "emoji": "📊",
                "page": "performance_review"
            },
            {
                "title": "Document Manager",
                "description": "View, export, and manage all generated documents",
                "emoji": "📚",
                "page": "document_manager"
            }
        ]

        # Create 2 columns for better responsive layout
        col1, col2 = st.columns(2)

        # Distribute features across columns
        for i, feature in enumerate(features):
            with col1 if i % 2 == 0 else col2:
                create_feature_card(**feature)
    else:
        render_form_page()

except Exception as e:
    st.error("Something went wrong! Please try again.")
    st.exception(e)

# Enhanced Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2rem;'>
        <p style='color: #888; font-size: 1.1rem; font-weight: 500;'>© 2024 HRCraft AI. All rights reserved.</p>
        <p style='color: #666; font-size: 1rem;'>Powered by AI | Built with ❤️</p>
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    pass
