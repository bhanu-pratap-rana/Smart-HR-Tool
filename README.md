# Smart HR Tool 🤖

AI-powered HR document generation tool with dual model support (Ollama + Groq).

## Features ✨

- **Job Description Generator** - Create professional job descriptions with AI
- **Offer Letter Generator** - Generate customized offer letters
- **Interview Questions Generator** - Get role-specific interview questions
- **Onboarding Plan Generator** - Design comprehensive onboarding experiences
- **Performance Review Generator** - Create detailed performance assessments
- **Document Manager** - View, export (PDF/DOCX), and manage all generated documents

## Architecture 🏗️

```
Smart-HR-Tool/
├── backend/           # FastAPI backend
│   └── app/
│       ├── api/       # API endpoints
│       ├── core/      # Core functionality
│       ├── models/    # Data models
│       └── services/  # Business logic
├── frontend/          # Streamlit UI
│   ├── pages/        # UI pages
│   └── utils/        # Helper functions
└── alembic/          # Database migrations
```

## Tech Stack 🛠️

### Backend
- **FastAPI** - Modern web framework
- **SQLModel** - Database ORM
- **Pydantic** - Data validation
- **Alembic** - Database migrations

### Frontend
- **Streamlit** - Interactive UI
- **python-docx** - DOCX generation
- **xhtml2pdf** - PDF generation

### AI Models
- **HRCraft Mini** (Ollama - deepseek-r1:8b) - Local, slower but free
- **HRCraft Pro** (Groq - llama-3.3-70b-versatile) - Cloud, fast responses

## Installation 🚀

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.ai/) (for local model)
- Groq API key (get free at [console.groq.com](https://console.groq.com))

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/bhanu-pratap-rana/Smart-HR-Tool.git
cd Smart-HR-Tool
```

2. **Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**

Create a `.env` file in the root directory:

```env
# Application
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Ollama (Local AI)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:8b
OLLAMA_TEMPERATURE=0.7
OLLAMA_MAX_TOKENS=2000

# Groq (Cloud AI)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.7
GROQ_MAX_TOKENS=2000
```

5. **Install Ollama model** (for local AI)
```bash
ollama pull deepseek-r1:8b
```

6. **Initialize database**
```bash
alembic upgrade head
```

## Running the Application 🎯

### Option 1: Using batch scripts (Windows)

**Start Backend:**
```bash
start_backend.bat
```

**Start Frontend** (in new terminal):
```bash
start_frontend.bat
```

### Option 2: Manual start

**Backend:**
```bash
venv\Scripts\activate
uvicorn backend.app.main:app --reload
```

**Frontend:**
```bash
venv\Scripts\activate
streamlit run frontend/app.py
```

## Access Points 🌐

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints 📡

- `POST /api/v1/job-description/generate` - Generate job description
- `POST /api/v1/offer-letter/generate` - Generate offer letter
- `POST /api/v1/interview-questions/generate` - Generate interview questions
- `POST /api/v1/onboarding/generate` - Generate onboarding plan
- `POST /api/v1/performance-review/generate` - Generate performance review
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/export/pdf/{id}` - Export as PDF
- `GET /api/v1/export/docx/{id}` - Export as DOCX

## Development 💻

### Project Structure

```
backend/app/
├── api/v1/endpoints/    # API route handlers
├── core/                # Exception handlers, utilities
├── models/              # Pydantic models & database models
├── services/            # Business logic (AI, rendering, etc.)
└── main.py             # FastAPI application

frontend/
├── pages/              # Streamlit pages
├── utils/              # Helper functions
└── app.py             # Main Streamlit app

alembic/
└── versions/          # Database migration files
```

### Adding New Features

1. Create database model in `backend/app/models/database.py`
2. Create request/response models in `backend/app/models/requests.py` & `responses.py`
3. Create endpoint in `backend/app/api/v1/endpoints/`
4. Register route in `backend/app/api/v1/router.py`
5. Create UI page in `frontend/pages/`
6. Add page to navigation in `frontend/app.py`

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License.

## Support 💬

For issues and questions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, Streamlit, and AI**
