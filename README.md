# Smart HR Assistant 🤖

An enterprise-grade AI-powered HR assistant that revolutionizes HR operations with state-of-the-art features and stunning visual animations.

## Core Features 🌟

- **Job Description Generator** - Create compelling JDs with AI assistance
- **Offer Letter Generator** - Generate professional offer letters instantly  
- **Interview Questions** - Get role-specific interview questions
- **Onboarding Plans** - Design comprehensive onboarding experiences
- **Performance Reviews** - Generate detailed performance assessments

## Tech Stack 🛠️

### Frontend
- Streamlit
- Custom CSS/Animations
- PDF Generation (xhtml2pdf)
- Word Doc Support (python-docx)
- Markdown Processing

### Backend  
- FastAPI
- Pydantic
- OpenAI Integration
- AsyncIO
- CORS Middleware

### AI Models
- ByticalGPT Mini - Fast responses
- ByticalGPT Versatile - Complex tasks

## Installation ⚡

1. Clone the repository
```bash
git clone https://github.com/bytical/smartHR.git
cd smartHR


Install dependencies
pip install -r requirements.txt

Configure environment variables in .env for openai and groq:
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

Running the Application 🚀
First, start the FastAPI backend:
python fastapi_server.py

Then launch the Streamlit frontend in a new terminal:
python -m streamlit run frontapp.py

Key Libraries 📚
# Frontend Dependencies
streamlit==1.24.0
requests==2.31.0
python-docx==0.8.11
xhtml2pdf==0.2.11
markdown==3.4.3

# Backend Dependencies
fastapi==0.100.0
uvicorn==0.22.0
python-dotenv==1.0.0
openai==0.27.8
pydantic==2.0.2
