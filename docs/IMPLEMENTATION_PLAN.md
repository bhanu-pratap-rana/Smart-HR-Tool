# 🚀 HRCraft AI - Complete Implementation Plan
**Based on FastAPI, SQLModel, Pydantic & Python-DOCX Best Practices**

---

## 📊 Executive Summary

This plan transforms HRCraft AI from a prototype into a production-ready HR document generation platform with:
- **One-time company setup** applied across all 5 document types
- **Professional templates** with logos, headers, footers
- **Reliable AI generation** with retries and fallbacks
- **Beautiful exports** (PDF + DOCX) with proper typography
- **Scalable architecture** using SQLModel for data persistence

---

## 🎯 Implementation Phases

### **Phase 0: Critical Fixes & Stabilization** (Week 1 - Days 1-3)
**Goal:** Fix immediate blocking issues

#### 0.1 Fix Groq API Service
**Issue:** `Client.__init__() got an unexpected keyword argument 'proxies'`

**Changes:**
```python
# backend/app/services/groq_service.py

class GroqService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.api_key = settings.groq_api_key
        self.model = settings.groq_model
        self.temperature = settings.groq_temperature
        self.max_tokens = settings.groq_max_tokens

        # Initialize client properly
        self.client = groq.Groq(api_key=self.api_key)

    def health_check(self) -> Dict[str, Any]:
        """Check if Groq service is available."""
        try:
            # Simple check without proxies
            return {
                "available": True,
                "model": self.model
            }
        except Exception as e:
            logger.warning(f"Groq health check failed: {e}")
            return {
                "available": False,
                "error": str(e)
            }
```

#### 0.2 Add Retry Logic with Exponential Backoff
**Best Practice:** FastAPI dependency injection for retries

```python
# backend/app/core/retry.py

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import groq
from typing import TypeVar, Callable

T = TypeVar('T')

def with_retry(
    max_attempts: int = 3,
    min_wait: int = 1,
    max_wait: int = 10
):
    """Decorator for retrying AI generation with exponential backoff."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            groq.APIConnectionError,
            groq.APITimeoutError,
            ConnectionError
        )),
        reraise=True
    )

# Usage in service:
class GroqService:
    @with_retry(max_attempts=3)
    def generate(self, prompt: str) -> str:
        """Generate with automatic retry."""
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return completion.choices[0].message.content
        except groq.RateLimitError as e:
            raise GroqRateLimitError(retry_after=60)
```

#### 0.3 Improve Error Responses
**Best Practice:** Pydantic models for structured errors

```python
# backend/app/models/responses.py

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: str
    message: str
    field: Optional[str] = None

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "GROQ_API_ERROR",
                    "message": "Failed to connect to Groq service"
                },
                "trace_id": "abc-123-def",
                "timestamp": "2024-11-08T10:30:00Z"
            }
        }
    )
```

#### 0.4 Enhanced Logging
```python
# backend/app/core/logging_config.py

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', None)
        }
        return json.dumps(log_data)

# Apply in main.py
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format='%(message)s'
)
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

**Deliverables:**
- ✅ Groq service fixed
- ✅ Retry logic implemented
- ✅ Structured error responses
- ✅ JSON logging enabled

---

### **Phase 1: Database & Company Profile** (Week 1 - Days 4-7)
**Goal:** Persistent storage for company data

#### 1.1 Setup SQLModel Database
**Best Practice:** SQLModel with FastAPI dependency injection

```python
# backend/app/db.py

from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

# Database URL from settings
sqlite_url = "sqlite:///./hrcraft.db"

# Create engine with connection pooling
engine = create_engine(
    sqlite_url,
    echo=True,  # Log SQL statements in dev
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

def create_db_and_tables():
    """Create all tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session

# Type alias for cleaner dependencies
SessionDep = Annotated[Session, Depends(get_session)]
```

#### 1.2 Company Profile Models
**Best Practice:** Separate Base, Table, Create, Update, Public models

```python
# backend/app/models/company.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict

class CompanyProfileBase(SQLModel):
    """Base model with shared fields."""
    name: str = Field(index=True, max_length=200)
    legal_name: Optional[str] = Field(default=None, max_length=300)
    tagline: Optional[str] = Field(default=None, max_length=500)
    industry: Optional[str] = Field(default=None, max_length=100)
    website: Optional[str] = Field(default=None, max_length=200)
    phone: Optional[str] = Field(default=None, max_length=50)
    email: str = Field(max_length=200)

    # Address
    address_line1: str = Field(max_length=300)
    address_line2: Optional[str] = Field(default=None, max_length=300)
    city: str = Field(max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="India", max_length=100)

    # Branding
    primary_color: str = Field(default="#FF8C42", max_length=7)
    secondary_color: str = Field(default="#EF629F", max_length=7)
    hr_contact_name: Optional[str] = Field(default=None, max_length=200)
    hr_contact_title: Optional[str] = Field(default=None, max_length=100)

class CompanyProfile(CompanyProfileBase, table=True):
    """Database table model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    logo_file_id: Optional[int] = Field(default=None, foreign_key="brandfile.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    logo: Optional["BrandFile"] = Relationship(back_populates="company_profiles")
    templates: List["DocumentTemplate"] = Relationship(back_populates="company")

class CompanyProfileCreate(CompanyProfileBase):
    """Model for creating company profile."""
    pass

class CompanyProfileUpdate(SQLModel):
    """Model for updating company profile (all fields optional)."""
    name: Optional[str] = None
    legal_name: Optional[str] = None
    tagline: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    hr_contact_name: Optional[str] = None
    hr_contact_title: Optional[str] = None

class CompanyProfilePublic(CompanyProfileBase):
    """Public model for API responses."""
    id: int
    logo_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BrandFile(SQLModel, table=True):
    """Table for brand assets (logos, watermarks)."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companyprofile.id")
    file_type: str = Field(max_length=20)  # 'logo', 'watermark', 'signature'
    filename: str = Field(max_length=255)
    path: str = Field(max_length=500)
    mime_type: str = Field(max_length=100)
    width_px: Optional[int] = None
    height_px: Optional[int] = None
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    company_profiles: List[CompanyProfile] = Relationship(back_populates="logo")

class DocumentTemplate(SQLModel, table=True):
    """Table for document templates."""
    id: Optional[int] = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="companyprofile.id")
    doc_type: str = Field(index=True, max_length=50)  # 'jd', 'offer', etc.
    name: str = Field(max_length=200)
    version: int = Field(default=1)
    content_json: str = Field(sa_type=sqlalchemy.Text)  # JSON structure
    content_html: str = Field(sa_type=sqlalchemy.Text)  # HTML template
    default_font: str = Field(default="Arial", max_length=100)
    margin_mm: int = Field(default=25)
    is_default: bool = Field(default=False)
    created_by: Optional[str] = Field(default=None, max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    company: CompanyProfile = Relationship(back_populates="templates")
```

#### 1.3 Company Profile API Endpoints
**Best Practice:** APIRouter with dependency injection

```python
# backend/app/api/v1/endpoints/company_profile.py

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlmodel import select
from typing import Optional
import shutil
from pathlib import Path

router = APIRouter(prefix="/company-profile", tags=["Company Profile"])

UPLOAD_DIR = Path("uploads/company_assets")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.get("", response_model=CompanyProfilePublic)
async def get_company_profile(session: SessionDep):
    """Get company profile (returns first/only profile)."""
    statement = select(CompanyProfile).limit(1)
    profile = session.exec(statement).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please create one first."
        )

    # Add logo URL if exists
    public_profile = CompanyProfilePublic.model_validate(profile)
    if profile.logo:
        public_profile.logo_url = f"/api/v1/company-profile/logo/{profile.logo.id}"

    return public_profile

@router.post("", response_model=CompanyProfilePublic, status_code=status.HTTP_201_CREATED)
async def create_company_profile(
    profile_data: CompanyProfileCreate,
    session: SessionDep
):
    """Create company profile (only one allowed)."""
    # Check if profile already exists
    existing = session.exec(select(CompanyProfile)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile already exists. Use PUT to update."
        )

    profile = CompanyProfile.model_validate(profile_data)
    session.add(profile)
    session.commit()
    session.refresh(profile)

    return CompanyProfilePublic.model_validate(profile)

@router.put("", response_model=CompanyProfilePublic)
async def update_company_profile(
    profile_data: CompanyProfileUpdate,
    session: SessionDep
):
    """Update company profile."""
    profile = session.exec(select(CompanyProfile)).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found"
        )

    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    session.add(profile)
    session.commit()
    session.refresh(profile)

    return CompanyProfilePublic.model_validate(profile)

@router.post("/logo", response_model=dict)
async def upload_logo(
    file: UploadFile = File(...),
    session: SessionDep = None
):
    """Upload company logo."""
    # Validate file type
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PNG and JPEG images are allowed"
        )

    # Validate file size (max 2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 2MB"
        )

    # Get company profile
    profile = session.exec(select(CompanyProfile)).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Create company profile first"
        )

    # Save file
    file_ext = Path(file.filename).suffix
    safe_filename = f"logo_{profile.id}{file_ext}"
    file_path = UPLOAD_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(contents)

    # Create BrandFile record
    brand_file = BrandFile(
        company_id=profile.id,
        file_type="logo",
        filename=file.filename,
        path=str(file_path),
        mime_type=file.content_type,
        size_bytes=len(contents)
    )
    session.add(brand_file)
    session.commit()
    session.refresh(brand_file)

    # Update profile
    profile.logo_file_id = brand_file.id
    session.add(profile)
    session.commit()

    return {
        "message": "Logo uploaded successfully",
        "file_id": brand_file.id,
        "url": f"/api/v1/company-profile/logo/{brand_file.id}"
    }

@router.get("/logo/{file_id}")
async def get_logo(file_id: int, session: SessionDep):
    """Serve logo file."""
    brand_file = session.get(BrandFile, file_id)

    if not brand_file or brand_file.file_type != "logo":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Logo not found"
        )

    return FileResponse(
        path=brand_file.path,
        media_type=brand_file.mime_type,
        filename=brand_file.filename
    )
```

#### 1.4 Update Main App
```python
# backend/app/main.py

from backend.app.db import create_db_and_tables
from backend.app.api.v1.endpoints import company_profile

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    create_db_and_tables()
    logger.info("Database tables created")
    yield

app = FastAPI(lifespan=lifespan)

# Include company profile router
app.include_router(company_profile.router, prefix="/api/v1")
```

**Deliverables:**
- ✅ SQLModel database setup
- ✅ Company profile CRUD API
- ✅ Logo upload endpoint
- ✅ File serving endpoint

---

### **Phase 2: Frontend Company Settings** (Week 2 - Days 1-3)
**Goal:** UI for one-time company setup

#### 2.1 Company Settings Page
**Best Practice:** Streamlit forms with validation

```python
# frontend/pages/company_settings.py

import streamlit as st
import requests
from PIL import Image
import io

API_BASE_URL = "http://localhost:8000/api/v1"

def company_settings_page():
    st.markdown("## 🏢 Company Settings")
    st.markdown("Configure your company information once - it will be used across all documents.")

    # Fetch existing profile
    try:
        response = requests.get(f"{API_BASE_URL}/company-profile")
        if response.status_code == 200:
            profile = response.json()
            is_new = False
        else:
            profile = {}
            is_new = True
    except:
        profile = {}
        is_new = True

    with st.form("company_profile_form"):
        st.markdown("### Basic Information")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Company Name *",
                value=profile.get("name", ""),
                placeholder="e.g., Acme Corporation"
            )
            legal_name = st.text_input(
                "Legal Name",
                value=profile.get("legal_name", ""),
                placeholder="e.g., Acme Corporation Pvt. Ltd."
            )
            industry = st.selectbox(
                "Industry",
                ["Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Retail", "Other"],
                index=0 if not profile.get("industry") else ["Technology", "Finance", "Healthcare", "Education", "Manufacturing", "Retail", "Other"].index(profile.get("industry", "Technology"))
            )

        with col2:
            tagline = st.text_input(
                "Tagline",
                value=profile.get("tagline", ""),
                placeholder="e.g., Innovation at Scale"
            )
            website = st.text_input(
                "Website",
                value=profile.get("website", ""),
                placeholder="https://www.example.com"
            )
            email = st.text_input(
                "HR Email *",
                value=profile.get("email", ""),
                placeholder="hr@example.com"
            )

        st.markdown("### Contact Information")

        col1, col2 = st.columns(2)

        with col1:
            phone = st.text_input(
                "Phone",
                value=profile.get("phone", ""),
                placeholder="+91 1234567890"
            )
            address_line1 = st.text_input(
                "Address Line 1 *",
                value=profile.get("address_line1", ""),
                placeholder="Building No., Street"
            )
            address_line2 = st.text_input(
                "Address Line 2",
                value=profile.get("address_line2", ""),
                placeholder="Landmark, Area"
            )

        with col2:
            city = st.text_input(
                "City *",
                value=profile.get("city", ""),
                placeholder="Mumbai"
            )
            state = st.text_input(
                "State",
                value=profile.get("state", ""),
                placeholder="Maharashtra"
            )
            postal_code = st.text_input(
                "Postal Code",
                value=profile.get("postal_code", ""),
                placeholder="400001"
            )

        st.markdown("### Branding")

        col1, col2 = st.columns(2)

        with col1:
            primary_color = st.color_picker(
                "Primary Color",
                value=profile.get("primary_color", "#FF8C42")
            )
            hr_contact_name = st.text_input(
                "HR Contact Name",
                value=profile.get("hr_contact_name", ""),
                placeholder="John Doe"
            )

        with col2:
            secondary_color = st.color_picker(
                "Secondary Color",
                value=profile.get("secondary_color", "#EF629F")
            )
            hr_contact_title = st.text_input(
                "HR Contact Title",
                value=profile.get("hr_contact_title", ""),
                placeholder="HR Manager"
            )

        submitted = st.form_submit_button(
            "Save Company Profile" if is_new else "Update Company Profile",
            type="primary"
        )

    if submitted:
        if not all([name, email, address_line1, city]):
            st.error("Please fill all required fields marked with *")
            return

        payload = {
            "name": name,
            "legal_name": legal_name,
            "tagline": tagline,
            "industry": industry,
            "website": website,
            "phone": phone,
            "email": email,
            "address_line1": address_line1,
            "address_line2": address_line2,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "country": "India",
            "primary_color": primary_color,
            "secondary_color": secondary_color,
            "hr_contact_name": hr_contact_name,
            "hr_contact_title": hr_contact_title
        }

        try:
            if is_new:
                response = requests.post(f"{API_BASE_URL}/company-profile", json=payload)
            else:
                response = requests.put(f"{API_BASE_URL}/company-profile", json=payload)

            if response.status_code in [200, 201]:
                st.success("✅ Company profile saved successfully!")
                st.rerun()
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Failed to save: {str(e)}")

    # Logo Upload Section
    if not is_new:
        st.markdown("---")
        st.markdown("### Company Logo")

        # Show current logo if exists
        if profile.get("logo_url"):
            try:
                logo_response = requests.get(f"{API_BASE_URL}{profile['logo_url']}")
                if logo_response.status_code == 200:
                    image = Image.open(io.BytesIO(logo_response.content))
                    st.image(image, width=200, caption="Current Logo")
            except:
                pass

        uploaded_file = st.file_uploader(
            "Upload Logo (PNG/JPG, max 2MB)",
            type=["png", "jpg", "jpeg"],
            help="Recommended: 400x400px minimum"
        )

        if uploaded_file and st.button("Upload Logo"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

            try:
                response = requests.post(f"{API_BASE_URL}/company-profile/logo", files=files)
                if response.status_code == 200:
                    st.success("✅ Logo uploaded successfully!")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Upload error: {str(e)}")
```

#### 2.2 Update Main App Navigation
```python
# frontend/app.py

# Add to sidebar
with st.sidebar:
    st.markdown("### 📋 Menu")

    if st.button("🏢 Company Settings", use_container_width=True):
        st.session_state.page = 'company_settings'
        st.rerun()

    st.markdown("---")
    st.markdown("### 📝 Generate Documents")
    # ... existing buttons

# Add to page router
def render_form_page():
    if st.session_state.page == 'company_settings':
        from pages.company_settings import company_settings_page
        company_settings_page()
    elif st.session_state.page == 'jd_generator':
        job_description_page()
    # ... rest
```

**Deliverables:**
- ✅ Company settings UI
- ✅ Logo upload interface
- ✅ Form validation
- ✅ Navigation integration

---

### **Phase 3: Professional Document Templates** (Week 2 - Days 4-7)
**Goal:** Beautiful DOCX/PDF exports with branding

#### 3.1 Document Renderer Service
**Best Practice:** Service layer for document generation

```python
# backend/app/services/document_renderer.py

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from typing import Dict, Any, Optional
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from jinja2 import Template

class DocumentRenderer:
    """Service for rendering professional documents with company branding."""

    def __init__(self, company_profile: CompanyProfile):
        self.company = company_profile
        self.templates_dir = Path("backend/app/templates")

    def render_docx(
        self,
        content: str,
        doc_type: str,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Render DOCX with company branding."""
        doc = Document()

        # Set document margins (1 inch all sides)
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Add header with logo and company name
        header = doc.sections[0].header
        header_para = header.paragraphs[0]

        # Logo (if exists)
        if self.company.logo:
            run = header_para.add_run()
            run.add_picture(
                self.company.logo.path,
                width=Inches(1.5)
            )

        # Company name
        header_para.add_run(f"\t{self.company.name}\n")
        if self.company.tagline:
            header_para.add_run(f"\t{self.company.tagline}")

        # Style header
        header_para.paragraph_format.tab_stops.add_tab_stop(Inches(3.0))
        header_para.style = doc.styles['Header']

        # Add title
        title_text = metadata.get('title', doc_type.replace('_', ' ').title())
        title = doc.add_heading(title_text, level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Add metadata (date, reference)
        metadata_para = doc.add_paragraph()
        metadata_para.add_run(f"Generated: {metadata.get('date', datetime.utcnow().strftime('%Y-%m-%d'))}\n")
        metadata_para.add_run(f"Reference: {metadata.get('reference', 'HR-DOC-001')}")
        metadata_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        doc.add_paragraph()  # Spacer

        # Add main content (convert from markdown)
        self._add_markdown_content(doc, content)

        # Add footer with company info
        footer = doc.sections[0].footer
        footer_para = footer.paragraphs[0]
        footer_para.text = (
            f"{self.company.address_line1}, {self.company.city}, {self.company.state} {self.company.postal_code}\n"
            f"Email: {self.company.email} | Website: {self.company.website or ''}\n"
            f"© {datetime.utcnow().year} {self.company.name}. All rights reserved."
        )
        footer_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer_para.style = doc.styles['Footer']

        # Save to bytes
        from io import BytesIO
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer.getvalue()

    def _add_markdown_content(self, doc: Document, content: str):
        """Parse markdown and add to document with proper formatting."""
        # Simple markdown parsing
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                continue

            # Headings
            if line.startswith('###'):
                doc.add_heading(line.replace('###', '').strip(), level=3)
            elif line.startswith('##'):
                doc.add_heading(line.replace('##', '').strip(), level=2)
            elif line.startswith('#'):
                doc.add_heading(line.replace('#', '').strip(), level=1)

            # Lists
            elif line.startswith('- ') or line.startswith('* '):
                doc.add_paragraph(line[2:], style='List Bullet')
            elif line.startswith('1. ') or line[0].isdigit() and '. ' in line:
                text = line.split('. ', 1)[1] if '. ' in line else line
                doc.add_paragraph(text, style='List Number')

            # Bold text
            elif '**' in line:
                para = doc.add_paragraph()
                parts = line.split('**')
                for i, part in enumerate(parts):
                    run = para.add_run(part)
                    if i % 2 == 1:  # Odd indices are bold
                        run.bold = True

            # Normal paragraph
            else:
                doc.add_paragraph(line)

    def render_pdf(
        self,
        content: str,
        doc_type: str,
        metadata: Dict[str, Any]
    ) -> bytes:
        """Render PDF with company branding using WeasyPrint."""
        # Load HTML template
        template_path = self.templates_dir / f"{doc_type}_template.html"

        if template_path.exists():
            with open(template_path) as f:
                template = Template(f.read())
        else:
            # Use default template
            template = Template(self._get_default_html_template())

        # Convert markdown to HTML
        content_html = markdown.markdown(
            content,
            extensions=['extra', 'codehilite', 'tables']
        )

        # Render template
        html_content = template.render(
            company=self.company,
            content=content_html,
            metadata=metadata,
            title=metadata.get('title', doc_type.replace('_', ' ').title()),
            date=metadata.get('date', datetime.utcnow().strftime('%Y-%m-%d')),
            reference=metadata.get('reference', 'HR-DOC-001')
        )

        # Generate PDF
        pdf_bytes = HTML(string=html_content).write_pdf(
            stylesheets=[CSS(string=self._get_pdf_styles())]
        )

        return pdf_bytes

    def _get_default_html_template(self) -> str:
        """Default HTML template for documents."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
</head>
<body>
    <header>
        {% if company.logo %}
        <img src="file://{{ company.logo.path }}" alt="Logo" class="logo">
        {% endif %}
        <div class="company-info">
            <h1>{{ company.name }}</h1>
            {% if company.tagline %}
            <p class="tagline">{{ company.tagline }}</p>
            {% endif %}
        </div>
    </header>

    <div class="document-header">
        <h2>{{ title }}</h2>
        <p class="metadata">
            Generated: {{ date }}<br>
            Reference: {{ reference }}
        </p>
    </div>

    <main>
        {{ content|safe }}
    </main>

    <footer>
        <p>
            {{ company.address_line1 }}, {{ company.city }}, {{ company.state }} {{ company.postal_code }}<br>
            Email: {{ company.email }} | Website: {{ company.website }}<br>
            © {{ date[:4] }} {{ company.name }}. All rights reserved.
        </p>
    </footer>
</body>
</html>
        """

    def _get_pdf_styles(self) -> str:
        """CSS styles for PDF rendering."""
        return f"""
        @page {{
            size: A4;
            margin: 25mm;

            @top-center {{
                content: "{self.company.name}";
                font-size: 10pt;
                color: #666;
            }}

            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
        }}

        body {{
            font-family: 'Arial', sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
        }}

        header {{
            display: flex;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 2px solid {self.company.primary_color};
            margin-bottom: 30px;
        }}

        .logo {{
            width: 100px;
            height: auto;
            margin-right: 20px;
        }}

        .company-info h1 {{
            color: {self.company.primary_color};
            margin: 0;
            font-size: 24pt;
        }}

        .tagline {{
            color: {self.company.secondary_color};
            font-style: italic;
            margin: 5px 0 0 0;
        }}

        .document-header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .document-header h2 {{
            color: {self.company.primary_color};
            font-size: 20pt;
            margin-bottom: 10px;
        }}

        .metadata {{
            color: #666;
            font-size: 10pt;
        }}

        main {{
            margin: 20px 0;
        }}

        h1, h2, h3 {{
            color: {self.company.primary_color};
            page-break-after: avoid;
        }}

        h1 {{ font-size: 18pt; }}
        h2 {{ font-size: 16pt; }}
        h3 {{ font-size: 14pt; }}

        p {{
            text-align: justify;
            margin-bottom: 10px;
        }}

        ul, ol {{
            margin: 10px 0 10px 20px;
        }}

        li {{
            margin-bottom: 5px;
        }}

        footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 9pt;
            color: #666;
            padding: 10px 0;
            border-top: 1px solid #ddd;
        }}
        """
```

#### 3.2 Export Endpoints
```python
# backend/app/api/v1/endpoints/exports.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from sqlmodel import select

router = APIRouter(prefix="/exports", tags=["Document Exports"])

@router.post("/docx")
async def export_docx(
    content: str,
    doc_type: str,
    metadata: Dict[str, Any],
    session: SessionDep
):
    """Export document as DOCX."""
    # Get company profile
    profile = session.exec(select(CompanyProfile)).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile required for exports"
        )

    # Render document
    renderer = DocumentRenderer(profile)
    docx_bytes = renderer.render_docx(content, doc_type, metadata)

    # Return as downloadable file
    filename = f"{doc_type}_{metadata.get('reference', 'document')}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/pdf")
async def export_pdf(
    content: str,
    doc_type: str,
    metadata: Dict[str, Any],
    session: SessionDep
):
    """Export document as PDF."""
    profile = session.exec(select(CompanyProfile)).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile required for exports"
        )

    renderer = DocumentRenderer(profile)
    pdf_bytes = renderer.render_pdf(content, doc_type, metadata)

    filename = f"{doc_type}_{metadata.get('reference', 'document')}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

**Deliverables:**
- ✅ DOCX renderer with branding
- ✅ PDF renderer with branding
- ✅ Export API endpoints
- ✅ Template system

---

### **Phase 4: Improve AI Prompts** (Week 3 - Days 1-2)
**Goal:** Better quality generated content

#### 4.1 Prompt Templates
```python
# backend/app/prompts/job_description.txt

You are a professional HR content writer with 10+ years of experience.

Create a comprehensive job description for:

COMPANY CONTEXT:
- Company: {{company_name}}
- Industry: {{industry}}
- Company Size: {{company_size}}

JOB DETAILS:
- Title: {{job_title}}
- Department: {{department}}
- Experience Level: {{exp_level}} years
- Location: {{location}}
- Salary Range: {{salary}}

REQUIREMENTS:
- Qualifications: {{qualification}}
- Required Skills: {{req_skills}}
- Key Responsibilities: {{role}}

FORMAT REQUIREMENTS:
1. Use clear, professional language
2. Be specific and measurable
3. Avoid generic phrases like "rockstar" or "ninja"
4. Include diversity statement
5. Structure with these EXACT sections:

## About [Company Name]
Brief company introduction (2-3 sentences)

## Role Overview
Concise summary of the position (2-3 sentences)

## Key Responsibilities
- List 5-7 specific, actionable responsibilities
- Use strong action verbs (Lead, Design, Implement, etc.)
- Be specific about outcomes

## Required Qualifications
**Education:**
- Specific degree requirements

**Experience:**
- Years and type of experience

**Technical Skills:**
- List each skill separately with proficiency level

**Soft Skills:**
- 3-5 key soft skills for the role

## Preferred Qualifications
- 2-3 nice-to-have qualifications

## What We Offer
**Compensation:**
- Salary: {{salary}}

**Benefits:**
- List 4-5 benefits specific to this role level

**Growth:**
- Career development opportunities

## Work Environment
- Location details
- Work model (Remote/Hybrid/Onsite)
- Team structure

## How to Apply
Standard application instructions

## Equal Opportunity Statement
[Company Name] is an equal opportunity employer committed to building a diverse and inclusive team. We encourage applications from candidates of all backgrounds.

OUTPUT ONLY THE JOB DESCRIPTION CONTENT. Do not include explanations or meta-commentary.
```

#### 4.2 Prompt Builder Service
```python
# backend/app/services/prompt_builder.py

from jinja2 import Template
from pathlib import Path
from typing import Dict, Any

class PromptBuilder:
    """Build structured prompts from templates."""

    def __init__(self):
        self.prompts_dir = Path("backend/app/prompts")

    def build_prompt(
        self,
        doc_type: str,
        data: Dict[str, Any],
        company_profile: Optional[CompanyProfile] = None
    ) -> str:
        """Build prompt from template and data."""
        template_path = self.prompts_dir / f"{doc_type}.txt"

        if not template_path.exists():
            raise ValueError(f"Prompt template not found: {doc_type}")

        with open(template_path) as f:
            template = Template(f.read())

        # Merge company data if available
        context = {**data}
        if company_profile:
            context.update({
                "company_name": company_profile.name,
                "industry": company_profile.industry,
                "company_size": "51-200"  # Can be added to profile later
            })

        return template.render(**context)
```

#### 4.3 Update Job Description Endpoint
```python
# backend/app/api/v1/endpoints/job_description.py

from backend.app.services.prompt_builder import PromptBuilder

@router.post("/generate")
async def generate_job_description(
    request: GenerateJDRequest,
    ollama: OllamaServiceDep,
    groq: GroqServiceDep,
    session: SessionDep
):
    """Generate job description with company context."""
    start_time = time.time()

    # Get company profile
    company = session.exec(select(CompanyProfile)).first()

    # Build structured prompt
    prompt_builder = PromptBuilder()
    prompt = prompt_builder.build_prompt(
        doc_type="job_description",
        data={
            "job_title": request.job_title,
            "department": request.department,
            "exp_level": request.exp_level,
            "qualification": request.qualification,
            "req_skills": ", ".join(request.req_skills),
            "role": request.role,
            "salary": request.salary,
            "location": request.location
        },
        company_profile=company
    )

    # Select service and generate
    service = ollama if request.model_choice == "hrcraft_mini" else groq
    content = service.generate(prompt)

    generation_time = time.time() - start_time

    return GeneratedContentResponse(
        content=content,
        model_used=service.get_model_info()["model"],
        generation_time=round(generation_time, 2)
    )
```

**Deliverables:**
- ✅ Structured prompt templates
- ✅ Prompt builder service
- ✅ Company context injection
- ✅ Better formatting instructions

---

### **Phase 5: Update Frontend for New Exports** (Week 3 - Days 3-5)
**Goal:** Use new export endpoints

#### 5.1 Update Job Description Generator
```python
# frontend/pages/job_description_generator.py

# Replace old download functions with API calls

def download_as_docx(content: str, metadata: dict):
    """Download as DOCX using backend service."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/exports/docx",
            json={
                "content": content,
                "doc_type": "job_description",
                "metadata": metadata
            }
        )

        if response.status_code == 200:
            st.download_button(
                label="📥 Download DOCX",
                data=response.content,
                file_name=f"job_description_{metadata['reference']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.error("Failed to generate DOCX")
    except Exception as e:
        st.error(f"Export error: {str(e)}")

def download_as_pdf(content: str, metadata: dict):
    """Download as PDF using backend service."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/exports/pdf",
            json={
                "content": content,
                "doc_type": "job_description",
                "metadata": metadata
            }
        )

        if response.status_code == 200:
            st.download_button(
                label="📥 Download PDF",
                data=response.content,
                file_name=f"job_description_{metadata['reference']}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Failed to generate PDF")
    except Exception as e:
        st.error(f"Export error: {str(e)}")

# Use in the main flow:
if response.status_code == 200:
    jd_content = response.json()["content"]
    st.success("Job Description generated successfully!")

    # Show content
    st.markdown("### Generated Job Description")
    st.markdown(jd_content)

    # Generate metadata
    metadata = {
        "title": "Job Description",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "reference": f"JD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        download_as_docx(jd_content, metadata)
    with col2:
        download_as_pdf(jd_content, metadata)
```

**Deliverables:**
- ✅ Frontend export integration
- ✅ Download buttons
- ✅ Metadata generation
- ✅ Error handling

---

### **Phase 6: Apply to All 5 Products** (Week 3 - Days 6-7)
**Goal:** Consistency across all document types

#### 6.1 Create Prompt Templates for Each Type
```
backend/app/prompts/
├── job_description.txt ✅
├── offer_letter.txt
├── interview_questions.txt
├── onboarding_plan.txt
└── performance_review.txt
```

#### 6.2 Update Each Generator Page
- Use new export endpoints
- Apply company branding
- Consistent UI/UX

**Deliverables:**
- ✅ 5 prompt templates
- ✅ All generators updated
- ✅ Consistent branding
- ✅ Professional exports

---

## 📦 Additional Dependencies

```txt
# Add to requirements.txt

# Database
sqlmodel==0.0.24
sqlalchemy==2.0.35

# Document Generation
python-docx==1.1.2
weasyprint==62.3
jinja2==3.1.4

# Retry Logic
tenacity==9.0.0

# Image Processing (for logo validation)
pillow==10.4.0
```

---

## ✅ Final Checklist

### Phase 0 (Critical Fixes)
- [ ] Groq service fixed
- [ ] Retry logic implemented
- [ ] Structured errors
- [ ] JSON logging

### Phase 1 (Database)
- [ ] SQLModel setup
- [ ] Company profile models
- [ ] CRUD endpoints
- [ ] Logo upload

### Phase 2 (Frontend Settings)
- [ ] Company settings page
- [ ] Form validation
- [ ] Logo upload UI
- [ ] Navigation

### Phase 3 (Templates)
- [ ] DOCX renderer
- [ ] PDF renderer
- [ ] Export endpoints
- [ ] Branding integration

### Phase 4 (AI Prompts)
- [ ] Prompt templates
- [ ] Prompt builder
- [ ] Company context
- [ ] Better structure

### Phase 5 (Frontend Exports)
- [ ] Export integration
- [ ] Download buttons
- [ ] Metadata handling

### Phase 6 (All Products)
- [ ] All prompts created
- [ ] All generators updated
- [ ] Consistent UX
- [ ] Testing complete

---

## 🚀 Success Metrics

1. **Quality:** Generated documents look professional (90%+ user satisfaction)
2. **Branding:** Company logo appears on all exports
3. **Reliability:** 95%+ generation success rate
4. **Performance:** <10s generation time
5. **User Experience:** One-time setup, reusable across products

---

## 📝 Next Steps After Phase 6

1. **Template Library** - Let users save custom templates
2. **Analytics** - Track usage, popular templates
3. **Rich Text Editor** - Edit before export
4. **Collaboration** - Share drafts, approvals
5. **Multi-language** - Generate in different languages

---

### **Phase 7: React Frontend Migration** (Week 4-5)
**Goal:** Transform Streamlit prototype into production-ready React SPA

Moving from Streamlit to React unlocks a professional SaaS experience with better UX, component reuse across 5 document workflows, and easier integration with design systems and role-based routing.

#### 7.1 Technology Stack Selection

**Framework:** Next.js 14+ with App Router
**State Management:** React Query + Zustand
**Forms:** React Hook Form + Zod
**Styling:** Tailwind CSS + shadcn/ui
**Rich Text:** TipTap or Slate
**Deployment:** Vercel (frontend) + Railway/Render (backend)

**Why This Stack:**
- Next.js App Router provides server components, built-in routing, and optimal performance
- React Query handles API caching, mutations, and optimistic updates
- Zustand manages UI preferences (lightweight, TypeScript-first)
- React Hook Form + Zod delivers type-safe form validation
- TipTap provides collaborative editing capabilities

#### 7.2 Project Structure

**Best Practice:** Next.js App Router with feature-based organization

```
hrcraft-frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with providers
│   ├── page.tsx                  # Dashboard home
│   ├── (auth)/                   # Auth route group
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/              # Protected routes
│   │   ├── layout.tsx            # Dashboard layout with sidebar
│   │   ├── company/              # Company settings
│   │   │   └── page.tsx
│   │   ├── generate/             # Document generation
│   │   │   ├── job-description/
│   │   │   │   └── page.tsx
│   │   │   ├── offer-letter/
│   │   │   ├── interview-questions/
│   │   │   ├── onboarding-plan/
│   │   │   └── performance-review/
│   │   └── documents/            # Document library
│   │       └── page.tsx
│   └── api/                      # API routes (if needed for BFF pattern)
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── forms/                    # Reusable form components
│   │   ├── JobDescriptionForm.tsx
│   │   ├── OfferLetterForm.tsx
│   │   └── CompanyProfileForm.tsx
│   ├── layouts/
│   │   ├── DashboardLayout.tsx
│   │   └── Sidebar.tsx
│   ├── document/
│   │   ├── DocumentPreview.tsx
│   │   ├── RichTextEditor.tsx
│   │   └── ExportButtons.tsx
│   └── shared/
│       ├── LoadingSpinner.tsx
│       └── ErrorBoundary.tsx
├── lib/
│   ├── api/                      # API client & React Query hooks
│   │   ├── client.ts
│   │   ├── hooks/
│   │   │   ├── useCompanyProfile.ts
│   │   │   ├── useGenerateDocument.ts
│   │   │   └── useExportDocument.ts
│   │   └── types.ts
│   ├── stores/                   # Zustand stores
│   │   ├── uiStore.ts
│   │   └── editorStore.ts
│   ├── validations/              # Zod schemas
│   │   ├── jobDescription.ts
│   │   ├── companyProfile.ts
│   │   └── common.ts
│   └── utils/
│       ├── cn.ts                 # Tailwind class names utility
│       └── formatters.ts
├── public/
│   └── images/
├── types/                        # TypeScript types
│   └── index.ts
└── package.json
```

#### 7.3 Root Layout with Providers

**Best Practice:** Centralized provider setup with React Query

```tsx
// app/layout.tsx
import './globals.css'
import { Inter } from 'next/font/google'
import { Providers } from '@/components/providers'
import type { Metadata } from 'next'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'HRCraft AI - Smart HR Document Generator',
  description: 'AI-powered HR document generation platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

```tsx
// components/providers.tsx
'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Toaster } from '@/components/ui/toaster'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            gcTime: 5 * 60 * 1000, // 5 minutes
            retry: 1,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

#### 7.4 API Client with React Query

**Best Practice:** Axios instance with React Query hooks

```typescript
// lib/api/client.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
})

// Request interceptor for auth tokens
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

```typescript
// lib/api/hooks/useCompanyProfile.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '../client'
import type { CompanyProfile, CompanyProfileCreate, CompanyProfileUpdate } from '../types'

const QUERY_KEY = ['companyProfile']

export function useCompanyProfile() {
  return useQuery({
    queryKey: QUERY_KEY,
    queryFn: async () => {
      const { data } = await apiClient.get<CompanyProfile>('/company-profile')
      return data
    },
    retry: false, // Don't retry if company profile doesn't exist yet
  })
}

export function useCreateCompanyProfile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (profileData: CompanyProfileCreate) => {
      const { data } = await apiClient.post<CompanyProfile>('/company-profile', profileData)
      return data
    },
    onSuccess: (data) => {
      // Update cache with new profile
      queryClient.setQueryData(QUERY_KEY, data)
      // Invalidate to refetch with logo URL
      queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })
}

export function useUpdateCompanyProfile() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (profileData: CompanyProfileUpdate) => {
      const { data } = await apiClient.put<CompanyProfile>('/company-profile', profileData)
      return data
    },
    onMutate: async (newProfile) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: QUERY_KEY })

      // Snapshot previous value for rollback
      const previousProfile = queryClient.getQueryData<CompanyProfile>(QUERY_KEY)

      // Optimistically update cache
      if (previousProfile) {
        queryClient.setQueryData<CompanyProfile>(QUERY_KEY, {
          ...previousProfile,
          ...newProfile,
        })
      }

      return { previousProfile }
    },
    onError: (err, variables, context) => {
      // Rollback on error
      if (context?.previousProfile) {
        queryClient.setQueryData(QUERY_KEY, context.previousProfile)
      }
    },
    onSettled: () => {
      // Refetch to ensure cache is in sync
      queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })
}

export function useUploadLogo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)

      const { data } = await apiClient.post('/company-profile/logo', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEY })
    },
  })
}
```

```typescript
// lib/api/hooks/useGenerateDocument.ts
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '../client'
import type { GenerateJDRequest, GeneratedContentResponse } from '../types'

export function useGenerateJobDescription() {
  return useMutation({
    mutationFn: async (request: GenerateJDRequest) => {
      const { data } = await apiClient.post<GeneratedContentResponse>(
        '/job-description/generate',
        request
      )
      return data
    },
  })
}

export function useExportDocument() {
  return useMutation({
    mutationFn: async ({
      content,
      docType,
      metadata,
      format,
    }: {
      content: string
      docType: string
      metadata: Record<string, any>
      format: 'docx' | 'pdf'
    }) => {
      const { data } = await apiClient.post(
        `/exports/${format}`,
        { content, doc_type: docType, metadata },
        { responseType: 'blob' }
      )
      return data
    },
  })
}
```

#### 7.5 Form Validation with React Hook Form + Zod

**Best Practice:** Type-safe forms with reusable schemas

```typescript
// lib/validations/jobDescription.ts
import { z } from 'zod'

export const jobDescriptionSchema = z.object({
  job_title: z.string().min(2, 'Job title must be at least 2 characters').max(100),
  department: z.string().min(2, 'Department is required').max(100),
  exp_level: z.number().int().min(0, 'Experience must be 0 or more').max(50),
  qualification: z.string().min(5, 'Qualifications are required'),
  req_skills: z.array(z.string()).min(1, 'At least one skill is required'),
  role: z.string().min(20, 'Role description must be at least 20 characters'),
  salary: z.string().min(1, 'Salary range is required'),
  location: z.string().min(2, 'Location is required'),
  model_choice: z.enum(['hrcraft_mini', 'hrcraft_pro']).default('hrcraft_mini'),
})

export type JobDescriptionFormData = z.infer<typeof jobDescriptionSchema>
```

```tsx
// components/forms/JobDescriptionForm.tsx
'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { jobDescriptionSchema, type JobDescriptionFormData } from '@/lib/validations/jobDescription'
import { useGenerateJobDescription } from '@/lib/api/hooks/useGenerateDocument'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form'
import { toast } from '@/components/ui/use-toast'
import { Loader2 } from 'lucide-react'

interface Props {
  onSuccess: (content: string, metadata: any) => void
}

export function JobDescriptionForm({ onSuccess }: Props) {
  const generateMutation = useGenerateJobDescription()

  const form = useForm<JobDescriptionFormData>({
    resolver: zodResolver(jobDescriptionSchema),
    defaultValues: {
      job_title: '',
      department: '',
      exp_level: 0,
      qualification: '',
      req_skills: [],
      role: '',
      salary: '',
      location: '',
      model_choice: 'hrcraft_mini',
    },
  })

  const onSubmit = async (data: JobDescriptionFormData) => {
    try {
      const result = await generateMutation.mutateAsync(data)

      toast({
        title: 'Success!',
        description: 'Job description generated successfully',
      })

      onSuccess(result.content, {
        title: 'Job Description',
        date: new Date().toISOString().split('T')[0],
        reference: `JD-${Date.now()}`,
      })
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to generate job description',
        variant: 'destructive',
      })
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="job_title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Job Title *</FormLabel>
                <FormControl>
                  <Input placeholder="e.g., Senior Python Developer" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="department"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Department *</FormLabel>
                <FormControl>
                  <Input placeholder="e.g., Engineering" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="exp_level"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Experience Level (years) *</FormLabel>
              <FormControl>
                <Input
                  type="number"
                  placeholder="0"
                  {...field}
                  onChange={(e) => field.onChange(parseInt(e.target.value))}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="qualification"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Required Qualifications *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="e.g., Bachelor's in Computer Science or equivalent"
                  rows={3}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Key Responsibilities *</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe main responsibilities..."
                  rows={5}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="salary"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Salary Range *</FormLabel>
                <FormControl>
                  <Input placeholder="e.g., $100k-150k" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="location"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Location *</FormLabel>
                <FormControl>
                  <Input placeholder="e.g., Remote or San Francisco, CA" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <FormField
          control={form.control}
          name="model_choice"
          render={({ field }) => (
            <FormItem>
              <FormLabel>AI Model</FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="hrcraft_mini">HRCraft Mini (Local, Fast)</SelectItem>
                  <SelectItem value="hrcraft_pro">HRCraft Pro (Cloud, Advanced)</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={generateMutation.isPending} className="w-full">
          {generateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {generateMutation.isPending ? 'Generating...' : 'Generate Job Description'}
        </Button>
      </form>
    </Form>
  )
}
```

#### 7.6 Zustand Store for UI State

**Best Practice:** Separate stores for different concerns

```typescript
// lib/stores/uiStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  toggleSidebar: () => void
  setTheme: (theme: 'light' | 'dark') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarCollapsed: false,
      theme: 'light',
      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'hrcraft-ui-preferences',
    }
  )
)
```

```typescript
// lib/stores/editorStore.ts
import { create } from 'zustand'

interface EditorState {
  content: string
  metadata: Record<string, any> | null
  setContent: (content: string) => void
  setMetadata: (metadata: Record<string, any>) => void
  reset: () => void
}

export const useEditorStore = create<EditorState>()((set) => ({
  content: '',
  metadata: null,
  setContent: (content) => set({ content }),
  setMetadata: (metadata) => set({ metadata }),
  reset: () => set({ content: '', metadata: null }),
}))
```

#### 7.7 Dashboard Layout with Sidebar

**Best Practice:** Nested layouts with App Router

```tsx
// app/(dashboard)/layout.tsx
import { DashboardLayout } from '@/components/layouts/DashboardLayout'

export default function Layout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>
}
```

```tsx
// components/layouts/DashboardLayout.tsx
'use client'

import { Sidebar } from './Sidebar'
import { useUIStore } from '@/lib/stores/uiStore'
import { cn } from '@/lib/utils/cn'

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { sidebarCollapsed } = useUIStore()

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main
        className={cn(
          'flex-1 overflow-y-auto transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <div className="container mx-auto p-8">{children}</div>
      </main>
    </div>
  )
}
```

```tsx
// components/layouts/Sidebar.tsx
'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useUIStore } from '@/lib/stores/uiStore'
import { cn } from '@/lib/utils/cn'
import {
  Building2,
  FileText,
  Mail,
  MessageSquare,
  UserCheck,
  ClipboardList,
  ChevronLeft,
} from 'lucide-react'

const navItems = [
  { href: '/company', label: 'Company Settings', icon: Building2 },
  { href: '/generate/job-description', label: 'Job Description', icon: FileText },
  { href: '/generate/offer-letter', label: 'Offer Letter', icon: Mail },
  { href: '/generate/interview-questions', label: 'Interview Questions', icon: MessageSquare },
  { href: '/generate/onboarding-plan', label: 'Onboarding Plan', icon: UserCheck },
  { href: '/generate/performance-review', label: 'Performance Review', icon: ClipboardList },
]

export function Sidebar() {
  const pathname = usePathname()
  const { sidebarCollapsed, toggleSidebar } = useUIStore()

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-white border-r border-gray-200 transition-all duration-300',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200">
        {!sidebarCollapsed && (
          <h1 className="text-xl font-bold text-primary">HRCraft AI</h1>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded hover:bg-gray-100"
          aria-label="Toggle sidebar"
        >
          <ChevronLeft className={cn('transition-transform', sidebarCollapsed && 'rotate-180')} />
        </button>
      </div>

      <nav className="p-4 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-gray-100 text-gray-700',
                sidebarCollapsed && 'justify-center'
              )}
            >
              <Icon className="h-5 w-5" />
              {!sidebarCollapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
```

#### 7.8 Document Generation Page

```tsx
// app/(dashboard)/generate/job-description/page.tsx
'use client'

import { useState } from 'react'
import { JobDescriptionForm } from '@/components/forms/JobDescriptionForm'
import { DocumentPreview } from '@/components/document/DocumentPreview'
import { ExportButtons } from '@/components/document/ExportButtons'
import { useEditorStore } from '@/lib/stores/editorStore'

export default function JobDescriptionPage() {
  const { content, metadata, setContent, setMetadata } = useEditorStore()

  const handleSuccess = (generatedContent: string, generatedMetadata: any) => {
    setContent(generatedContent)
    setMetadata(generatedMetadata)
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold">Generate Job Description</h1>
        <p className="text-gray-600 mt-2">
          Create professional job descriptions powered by AI
        </p>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="space-y-6">
          <JobDescriptionForm onSuccess={handleSuccess} />
        </div>

        <div className="space-y-6">
          {content ? (
            <>
              <DocumentPreview content={content} />
              <ExportButtons
                content={content}
                docType="job_description"
                metadata={metadata}
              />
            </>
          ) : (
            <div className="flex items-center justify-center h-full border-2 border-dashed border-gray-300 rounded-lg">
              <p className="text-gray-500">Preview will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

#### 7.9 Rich Text Editor Integration (Optional Enhancement)

**Best Practice:** TipTap for collaborative editing

```tsx
// components/document/RichTextEditor.tsx
'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { Button } from '@/components/ui/button'
import { Bold, Italic, List, ListOrdered, Heading2 } from 'lucide-react'

interface Props {
  content: string
  onChange: (content: string) => void
}

export function RichTextEditor({ content, onChange }: Props) {
  const editor = useEditor({
    extensions: [StarterKit],
    content,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
  })

  if (!editor) return null

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="bg-gray-50 border-b p-2 flex gap-2">
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'bg-gray-200' : ''}
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'bg-gray-200' : ''}
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive('heading', { level: 2 }) ? 'bg-gray-200' : ''}
        >
          <Heading2 className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'bg-gray-200' : ''}
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'bg-gray-200' : ''}
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
      </div>
      <EditorContent editor={editor} className="prose max-w-none p-4" />
    </div>
  )
}
```

#### 7.10 Multi-Tenant Architecture Preparation

**Best Practice:** Database schema and API design for multi-tenancy

```sql
-- Add to Phase 1 database schema

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(50) DEFAULT 'user', -- 'admin', 'user', 'viewer'
    company_id INTEGER REFERENCES company_profile(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Update company_profile table
ALTER TABLE company_profile ADD COLUMN owner_id INTEGER REFERENCES users(id);
ALTER TABLE company_profile ADD COLUMN subscription_tier VARCHAR(50) DEFAULT 'free';
ALTER TABLE company_profile ADD COLUMN max_documents_per_month INTEGER DEFAULT 50;
```

```python
# backend/app/models/user.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    full_name: Optional[str] = Field(default=None, max_length=200)
    role: str = Field(default="user", max_length=50)
    company_id: Optional[int] = Field(default=None, foreign_key="companyprofile.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    company: Optional["CompanyProfile"] = Relationship(back_populates="users")
```

#### 7.11 Deployment Strategy

**Frontend (Vercel):**
```bash
# vercel.json
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.hrcraft.com/api/v1"
  }
}
```

**Backend (Railway/Render):**
```dockerfile
# Dockerfile for FastAPI backend
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deliverables:**
- ✅ Next.js project scaffolded
- ✅ React Query API integration
- ✅ Form validation with Zod
- ✅ Zustand state management
- ✅ Dashboard layout with sidebar
- ✅ 5 document generation pages
- ✅ Company settings page
- ✅ Rich text editor (optional)
- ✅ Multi-tenant schema
- ✅ Deployment configs

---

**Ready to start implementation?**
Begin with Phase 0 fixes, then move systematically through each phase! 🎯
