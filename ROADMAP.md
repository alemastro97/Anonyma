# 🗺️ Anonyma Roadmap: Evolution to Enterprise Product

> **Vision**: Transform Anonyma from a text-only anonymization tool into a comprehensive, enterprise-grade document processing platform capable of detecting and anonymizing PII across all document formats.

---

## 📊 Current State Assessment

### ✅ What Works
- Core PII detection engine (Presidio + Flair + regex patterns)
- Italian-specific pattern support (Codice Fiscale, Partita IVA, CAP)
- Three anonymization modes (REDACT, SUBSTITUTE, VISUAL_REDACT)
- Ensemble detector with fallback mechanisms
- Basic Docker setup

### ❌ Critical Gaps
- **Document Support**: Only processes plain text strings
- **API Layer**: No REST/gRPC endpoints for integration
- **Testing**: Minimal test coverage (~5%)
- **Logging**: Uses `print()` statements instead of proper logging
- **Configuration**: All settings hardcoded in source
- **Security**: Mapping data not encrypted, potential leakage
- **Performance**: Models loaded repeatedly (~600MB per instance)
- **Scalability**: No async processing, caching, or batch support

---

## 🎯 Strategic Goals

1. **Document Format Support**: Process PDFs, images, Word, Excel, emails
2. **Production Readiness**: Proper logging, testing, error handling, security
3. **API-First Architecture**: RESTful API for easy integration
4. **Enterprise Features**: Multi-tenancy, audit trails, compliance
5. **Performance**: GPU support, model caching, batch processing
6. **Developer Experience**: Comprehensive docs, examples, SDKs

---

## 📅 Development Phases

### **PHASE 1: Foundation & Quality**
**Timeline**: Weeks 1-3 | **Status**: 🔴 Not Started | **Priority**: 🔥 CRITICAL

#### Objectives
- Establish production-grade infrastructure
- Achieve >80% test coverage
- Implement proper observability
- Refactor for maintainability

#### Deliverables

##### 1.1 Logging System Overhaul
**Effort**: 1 day | **Files**: All `*.py` files

- [ ] Replace all `print()` statements with `logging` module
- [ ] Implement structured logging (JSON format)
- [ ] Create `anonyma_core/logging/config.py` for log configuration
- [ ] Add contextual logging (correlation IDs, user tracking)
- [ ] Configure log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- [ ] Remove emoji from logs (professional output)

**Example**:
```python
# Before
print("🎭 Initializing Anonyma Engine...")

# After
logger.info("Initializing Anonyma Engine", extra={
    "component": "engine",
    "use_ensemble": use_ensemble
})
```

##### 1.2 Configuration Management System
**Effort**: 2 days | **New Files**: `config/`, `anonyma_core/config.py`

- [ ] Create YAML-based configuration system
- [ ] Implement environment variable overrides
- [ ] Add Pydantic models for config validation
- [ ] Support multiple environments (dev/staging/prod)
- [ ] Externalize all hardcoded values

**Config Structure**:
```
config/
├── config.yaml           # Base configuration
├── config.dev.yaml       # Development overrides
├── config.prod.yaml      # Production overrides
└── logging.yaml          # Logging configuration
```

**Key Settings**:
```yaml
detection:
  confidence_threshold: 0.7
  use_ensemble: false
  enable_italian_patterns: true

models:
  flair:
    models: ["ner-multi", "ner-english-ontonotes-fast"]
    cache_dir: ".flair_cache"
    device: "cpu"  # or "cuda"

anonymization:
  default_mode: "redact"
  redaction_character: "█"
  enable_reversibility: true

performance:
  max_text_length: 10000000  # 10MB
  batch_size: 32
  enable_caching: true
  cache_ttl: 3600
```

##### 1.3 Error Handling & Validation
**Effort**: 2 days | **Files**: All core modules

- [ ] Create `anonyma_core/exceptions.py` with custom exceptions
- [ ] Add try-catch blocks to all public APIs
- [ ] Implement input validation with Pydantic
- [ ] Add graceful degradation for detector failures
- [ ] Create error recovery strategies

**Custom Exceptions**:
```python
class AnonymaException(Exception):
    """Base exception"""

class DetectionError(AnonymaException):
    """Detection failed"""

class AnonymizationError(AnonymaException):
    """Anonymization failed"""

class ConfigurationError(AnonymaException):
    """Invalid configuration"""

class DocumentProcessingError(AnonymaException):
    """Document processing failed"""
```

##### 1.4 Comprehensive Testing Suite
**Effort**: 5 days | **New Directory**: `tests/`

- [ ] Create test directory structure
- [ ] Write unit tests for all detectors (>80% coverage)
- [ ] Write unit tests for all anonymization modes
- [ ] Add integration tests for engine workflows
- [ ] Create test fixtures and mock data
- [ ] Add edge case tests (empty, Unicode, overlaps)
- [ ] Set up pytest configuration
- [ ] Add coverage reporting

**Test Structure**:
```
tests/
├── unit/
│   ├── test_detectors.py       # Detector tests
│   ├── test_modes.py            # Mode tests
│   ├── test_engine.py           # Engine tests
│   └── test_config.py           # Config tests
├── integration/
│   ├── test_end_to_end.py       # E2E workflows
│   └── test_pipeline.py         # Pipeline tests
├── fixtures/
│   ├── test_data.py             # Sample texts
│   └── mock_models.py           # Model mocks
└── conftest.py                  # Pytest config
```

##### 1.5 Code Quality Tooling
**Effort**: 1 day | **New Files**: `.pre-commit-config.yaml`, `pyproject.toml`

- [ ] Configure `black` for code formatting
- [ ] Configure `isort` for import sorting
- [ ] Add `mypy` for static type checking
- [ ] Configure `ruff` or `pylint` for linting
- [ ] Set up pre-commit hooks
- [ ] Add type hints to all functions

**Tools Configuration**:
```toml
[tool.black]
line-length = 100
target-version = ['py311']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=anonyma_core --cov-report=html --cov-report=term"
```

##### 1.6 Architecture Refactoring
**Effort**: 3 days | **Files**: Core modules

- [ ] Create `BaseDetector` abstract class
- [ ] Create `BaseAnonymizationMode` abstract class
- [ ] Implement factory pattern for detectors
- [ ] Implement strategy pattern for modes
- [ ] Decouple engine from specific implementations
- [ ] Add plugin registration system

**Base Interfaces**:
```python
# anonyma_core/detectors/base.py
from abc import ABC, abstractmethod
from typing import List
from anonyma_core.types import Detection

class BaseDetector(ABC):
    """Base class for all PII detectors"""

    @abstractmethod
    def detect(self, text: str, language: str = 'it') -> List[Detection]:
        """Detect PII entities in text"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Detector name"""
        pass

# anonyma_core/modes/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAnonymizationMode(ABC):
    """Base class for anonymization modes"""

    @abstractmethod
    def anonymize(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Anonymize text based on detections"""
        pass

    @property
    @abstractmethod
    def mode_name(self) -> str:
        """Mode identifier"""
        pass
```

#### Success Metrics
- ✅ Zero `print()` statements in codebase
- ✅ >80% test coverage
- ✅ All config externalized
- ✅ Type hints on all public APIs
- ✅ Pre-commit hooks passing

---

### **PHASE 2: Document Processing Pipeline**
**Timeline**: Weeks 4-7 | **Status**: 🔴 Not Started | **Priority**: 🔥 CRITICAL

#### Objectives
- Support multiple document formats
- Preserve document formatting and metadata
- Handle OCR for scanned documents
- Create unified processing pipeline

#### Deliverables

##### 2.1 Document Abstraction Layer
**Effort**: 3 days | **New Module**: `anonyma_core/documents/`

- [ ] Create `BaseDocument` abstract class
- [ ] Implement document type detection
- [ ] Define metadata preservation interface
- [ ] Create document factory pattern

**Core Abstraction**:
```python
# anonyma_core/documents/base.py
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from enum import Enum

class DocumentFormat(Enum):
    PDF = "pdf"
    IMAGE = "image"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    EMAIL = "email"
    TEXT = "text"
    HTML = "html"

class BaseDocument(ABC):
    """Abstract base for all document types"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.metadata: Dict[str, Any] = {}
        self.format: DocumentFormat = self._detect_format()

    @abstractmethod
    def extract_text(self) -> str:
        """Extract plain text from document"""
        pass

    @abstractmethod
    def rebuild(self, anonymized_text: str, detections: List[Detection]) -> bytes:
        """Rebuild document with anonymized content"""
        pass

    @abstractmethod
    def _detect_format(self) -> DocumentFormat:
        """Detect document format"""
        pass

    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """Extract document metadata"""
        pass
```

##### 2.2 PDF Support (Priority #1)
**Effort**: 5 days | **New File**: `anonyma_core/documents/pdf_document.py`

**Dependencies**: `pdfplumber`, `PyPDF2`, `reportlab`, `pdf2image`, `pytesseract`

- [ ] Install PDF processing libraries
- [ ] Implement text extraction with position tracking
- [ ] Handle multi-page PDFs
- [ ] Preserve formatting (fonts, colors, layout)
- [ ] Support both digital and scanned PDFs (OCR)
- [ ] Implement PDF reconstruction with redactions
- [ ] Handle embedded images and forms
- [ ] Preserve document metadata

**Implementation**:
```python
# anonyma_core/documents/pdf_document.py
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pdf2image import convert_from_path
import pytesseract

class PDFDocument(BaseDocument):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.pdf = pdfplumber.open(file_path)
        self.is_scanned = self._is_scanned()

    def extract_text(self) -> str:
        """Extract text from PDF"""
        if self.is_scanned:
            return self._extract_with_ocr()
        return self._extract_digital()

    def _extract_digital(self) -> str:
        """Extract from digital PDF"""
        text = ""
        for page in self.pdf.pages:
            text += page.extract_text() + "\n"
        return text

    def _extract_with_ocr(self) -> str:
        """Extract from scanned PDF using OCR"""
        images = convert_from_path(self.file_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image, lang='ita+eng') + "\n"
        return text

    def rebuild(self, anonymized_text: str, detections: List[Detection]) -> bytes:
        """Rebuild PDF with redactions"""
        # Create new PDF with anonymized text
        # Preserve original layout and formatting
        pass

    def _is_scanned(self) -> bool:
        """Detect if PDF is scanned"""
        # Check if pages contain text or just images
        pass
```

**Features**:
- ✅ Text extraction from digital PDFs
- ✅ OCR for scanned PDFs
- ✅ Multi-page support
- ✅ Layout preservation
- ✅ Metadata preservation
- ✅ Form field handling
- ✅ Image handling

##### 2.3 Image/OCR Support (Priority #2)
**Effort**: 4 days | **New File**: `anonyma_core/documents/image_document.py`

**Dependencies**: `pytesseract`, `easyocr`, `Pillow`, `opencv-python`

- [ ] Install OCR libraries and language packs
- [ ] Implement text extraction with bounding boxes
- [ ] Support multiple languages (Italian, English)
- [ ] Handle various image formats (PNG, JPG, TIFF)
- [ ] Implement visual redaction (black boxes over PII)
- [ ] Optimize image quality for OCR
- [ ] Handle rotated/skewed images

**Implementation**:
```python
# anonyma_core/documents/image_document.py
import pytesseract
import easyocr
from PIL import Image, ImageDraw
import cv2
import numpy as np

class ImageDocument(BaseDocument):
    def __init__(self, file_path: Path, ocr_engine: str = "easyocr"):
        super().__init__(file_path)
        self.image = Image.open(file_path)
        self.ocr_engine = ocr_engine
        self.reader = None
        if ocr_engine == "easyocr":
            self.reader = easyocr.Reader(['it', 'en'])

    def extract_text(self) -> str:
        """Extract text with OCR"""
        if self.ocr_engine == "easyocr":
            return self._extract_with_easyocr()
        return self._extract_with_tesseract()

    def _extract_with_easyocr(self) -> str:
        """Extract using EasyOCR (better for Italian)"""
        results = self.reader.readtext(str(self.file_path))
        text = " ".join([result[1] for result in results])
        return text

    def _extract_with_tesseract(self) -> str:
        """Extract using Tesseract"""
        return pytesseract.image_to_string(self.image, lang='ita+eng')

    def rebuild(self, anonymized_text: str, detections: List[Detection]) -> bytes:
        """Create image with visual redactions"""
        img = self.image.copy()
        draw = ImageDraw.Draw(img)

        # Get bounding boxes for detected PII
        boxes = self._get_bounding_boxes(detections)

        # Draw black rectangles over PII
        for box in boxes:
            draw.rectangle(box, fill='black')

        # Save to bytes
        from io import BytesIO
        buffer = BytesIO()
        img.save(buffer, format=self.image.format)
        return buffer.getvalue()

    def _get_bounding_boxes(self, detections: List[Detection]) -> List[tuple]:
        """Map text detections to image coordinates"""
        # Use OCR bounding box data to locate text positions
        pass
```

**Features**:
- ✅ Multiple OCR engines (Tesseract, EasyOCR)
- ✅ Bounding box detection
- ✅ Visual redaction (black boxes)
- ✅ Multi-language support
- ✅ Image preprocessing (deskew, denoise)
- ✅ Format preservation

##### 2.4 Word Document Support (Priority #3)
**Effort**: 3 days | **New File**: `anonyma_core/documents/word_document.py`

**Dependencies**: `python-docx`, `docx2txt`

- [ ] Install Word processing libraries
- [ ] Extract text from .docx files
- [ ] Preserve formatting (bold, italic, colors)
- [ ] Handle tables and lists
- [ ] Preserve headers/footers
- [ ] Rebuild document with anonymization
- [ ] Support .doc files (via LibreOffice conversion)

**Implementation**:
```python
# anonyma_core/documents/word_document.py
from docx import Document
import docx2txt

class WordDocument(BaseDocument):
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.doc = Document(file_path)

    def extract_text(self) -> str:
        """Extract text from Word document"""
        text = ""
        for paragraph in self.doc.paragraphs:
            text += paragraph.text + "\n"

        # Extract from tables
        for table in self.doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text += cell.text + " "
            text += "\n"

        return text

    def rebuild(self, anonymized_text: str, detections: List[Detection]) -> bytes:
        """Rebuild Word document with anonymization"""
        # Create new document preserving styles
        # Replace detected PII with redactions
        pass
```

##### 2.5 Excel Support
**Effort**: 3 days | **New File**: `anonyma_core/documents/excel_document.py`

**Dependencies**: `openpyxl`, `pandas`

- [ ] Extract text from cells
- [ ] Handle multiple sheets
- [ ] Preserve formulas (anonymize only values)
- [ ] Handle charts and pivot tables
- [ ] Rebuild with anonymized data

##### 2.6 Email Support
**Effort**: 2 days | **New File**: `anonyma_core/documents/email_document.py`

**Dependencies**: `email`, `mailparser`

- [ ] Parse email headers
- [ ] Extract body (HTML and plain text)
- [ ] Handle attachments
- [ ] Anonymize sender/recipient
- [ ] Rebuild email message

##### 2.7 Unified Document Pipeline
**Effort**: 3 days | **New File**: `anonyma_core/documents/pipeline.py`

- [ ] Create document factory (auto-detect format)
- [ ] Implement unified processing workflow
- [ ] Add batch document processing
- [ ] Handle processing errors gracefully
- [ ] Add progress tracking

**Pipeline Implementation**:
```python
# anonyma_core/documents/pipeline.py
from pathlib import Path
from typing import Optional, List
import magic  # python-magic for file type detection

class DocumentPipeline:
    """Unified pipeline for processing any document format"""

    def __init__(self, engine: AnonymaEngine):
        self.engine = engine
        self.handlers = {
            DocumentFormat.PDF: PDFDocument,
            DocumentFormat.IMAGE: ImageDocument,
            DocumentFormat.WORD: WordDocument,
            DocumentFormat.EXCEL: ExcelDocument,
            DocumentFormat.EMAIL: EmailDocument,
        }

    def process(
        self,
        file_path: Path,
        mode: AnonymizationMode,
        output_path: Optional[Path] = None
    ) -> ProcessingResult:
        """Process any document format"""

        # 1. Detect document format
        doc_format = self._detect_format(file_path)
        logger.info(f"Detected format: {doc_format}", extra={"file": str(file_path)})

        # 2. Load appropriate handler
        handler_class = self.handlers.get(doc_format)
        if not handler_class:
            raise DocumentProcessingError(f"Unsupported format: {doc_format}")

        handler = handler_class(file_path)

        # 3. Extract text
        logger.info("Extracting text from document")
        text = handler.extract_text()

        # 4. Anonymize text
        logger.info("Anonymizing extracted text")
        result = self.engine.anonymize(text, mode)

        # 5. Rebuild document
        logger.info("Rebuilding document with anonymization")
        output_data = handler.rebuild(result.anonymized_text, result.detections)

        # 6. Save output
        if output_path:
            output_path.write_bytes(output_data)

        return ProcessingResult(
            original_file=file_path,
            output_file=output_path,
            format=doc_format,
            detections=result.detections,
            anonymized_text=result.anonymized_text,
            metadata=handler.metadata
        )

    def _detect_format(self, file_path: Path) -> DocumentFormat:
        """Detect document format using magic numbers"""
        mime = magic.from_file(str(file_path), mime=True)

        format_map = {
            'application/pdf': DocumentFormat.PDF,
            'image/png': DocumentFormat.IMAGE,
            'image/jpeg': DocumentFormat.IMAGE,
            'image/tiff': DocumentFormat.IMAGE,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocumentFormat.WORD,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': DocumentFormat.EXCEL,
            'message/rfc822': DocumentFormat.EMAIL,
        }

        return format_map.get(mime, DocumentFormat.TEXT)

    def process_batch(
        self,
        file_paths: List[Path],
        mode: AnonymizationMode,
        output_dir: Path
    ) -> List[ProcessingResult]:
        """Process multiple documents"""
        results = []
        for file_path in file_paths:
            try:
                output_path = output_dir / f"anonymized_{file_path.name}"
                result = self.process(file_path, mode, output_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append(ProcessingResult(
                    original_file=file_path,
                    error=str(e)
                ))
        return results
```

#### Success Metrics
- ✅ Support for 5+ document formats
- ✅ >95% text extraction accuracy
- ✅ Layout/formatting preservation
- ✅ OCR accuracy >90% for Italian text
- ✅ Batch processing capability

#### Dependencies to Add
```txt
# requirements/documents.txt
pdfplumber>=0.10.0
PyPDF2>=3.0.0
reportlab>=4.0.0
pdf2image>=1.16.0
pytesseract>=0.3.10
easyocr>=1.7.0
Pillow>=10.0.0
opencv-python>=4.8.0
python-docx>=0.8.11
openpyxl>=3.1.0
python-pptx>=0.6.21
python-magic>=0.4.27
mailparser>=3.15.0
```

---

### **PHASE 3: API & Service Layer**
**Timeline**: Weeks 8-10 | **Status**: 🔴 Not Started | **Priority**: 🔥 HIGH

#### Objectives
- Create production-ready REST API
- Enable async processing for large files
- Implement job queue system
- Add authentication and rate limiting

#### Deliverables

##### 3.1 REST API with FastAPI
**Effort**: 5 days | **New Module**: `anonyma_api/`

- [ ] Install FastAPI and dependencies
- [ ] Create API application structure
- [ ] Implement text anonymization endpoint
- [ ] Implement document upload endpoint
- [ ] Add batch processing endpoint
- [ ] Create job status endpoint
- [ ] Add health check endpoints
- [ ] Implement OpenAPI documentation

**API Structure**:
```
anonyma_api/
├── __init__.py
├── main.py                 # FastAPI app
├── routes/
│   ├── __init__.py
│   ├── text.py             # Text anonymization
│   ├── document.py         # Document processing
│   ├── batch.py            # Batch operations
│   └── jobs.py             # Job management
├── models/
│   ├── __init__.py
│   ├── requests.py         # Request models
│   └── responses.py        # Response models
├── middleware/
│   ├── __init__.py
│   ├── auth.py             # Authentication
│   ├── rate_limit.py       # Rate limiting
│   └── logging.py          # Request logging
├── services/
│   ├── __init__.py
│   └── anonymization.py    # Business logic
└── config.py               # API configuration
```

**Core Endpoints**:
```python
# anonyma_api/main.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional
import uuid

app = FastAPI(
    title="Anonyma API",
    description="Enterprise Document Anonymization Service",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Health checks
@app.get("/health")
async def health_check():
    """Health check for K8s liveness probe"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/ready")
async def readiness_check():
    """Readiness check for K8s readiness probe"""
    # Check if models are loaded
    return {"status": "ready", "models_loaded": True}

# Text anonymization
@app.post("/v1/anonymize/text", response_model=AnonymizationResponse)
async def anonymize_text(request: TextAnonymizationRequest):
    """
    Anonymize plain text

    - **text**: Input text to anonymize
    - **mode**: Anonymization mode (redact, substitute, visual_redact)
    - **language**: Text language (it, en)
    """
    try:
        engine = AnonymaEngine(use_ensemble=request.use_ensemble)
        result = engine.anonymize(
            text=request.text,
            mode=request.mode,
            language=request.language
        )
        return AnonymizationResponse(
            anonymized_text=result.anonymized_text,
            detections=result.detections,
            mode=result.mode,
            processing_time=result.processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Document anonymization
@app.post("/v1/anonymize/document", response_model=DocumentJobResponse)
async def anonymize_document(
    file: UploadFile = File(...),
    mode: AnonymizationMode = AnonymizationMode.REDACT,
    background_tasks: BackgroundTasks = None
):
    """
    Anonymize a document (PDF, Word, Excel, Image, etc.)

    Returns a job ID for tracking processing status
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file
    file_path = f"/tmp/uploads/{job_id}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Queue processing task
    background_tasks.add_task(
        process_document_async,
        job_id=job_id,
        file_path=file_path,
        mode=mode
    )

    return DocumentJobResponse(
        job_id=job_id,
        status="queued",
        message="Document processing queued"
    )

# Job status
@app.get("/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Check processing job status"""
    job = get_job_from_db(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job.status,
        progress=job.progress,
        result_url=job.result_url if job.status == "completed" else None,
        error=job.error if job.status == "failed" else None
    )

# Download result
@app.get("/v1/jobs/{job_id}/download")
async def download_result(job_id: str):
    """Download anonymized document"""
    job = get_job_from_db(job_id)
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="Result not available")

    return FileResponse(
        path=job.output_path,
        filename=f"anonymized_{job.original_filename}",
        media_type="application/octet-stream"
    )

# Batch processing
@app.post("/v1/anonymize/batch", response_model=BatchJobResponse)
async def anonymize_batch(
    files: List[UploadFile] = File(...),
    mode: AnonymizationMode = AnonymizationMode.REDACT,
    background_tasks: BackgroundTasks = None
):
    """
    Process multiple documents in batch

    Returns a batch job ID for tracking all files
    """
    batch_id = str(uuid.uuid4())
    job_ids = []

    for file in files:
        job_id = str(uuid.uuid4())
        file_path = f"/tmp/uploads/{job_id}_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        background_tasks.add_task(
            process_document_async,
            job_id=job_id,
            file_path=file_path,
            mode=mode,
            batch_id=batch_id
        )

        job_ids.append(job_id)

    return BatchJobResponse(
        batch_id=batch_id,
        job_ids=job_ids,
        total_files=len(files),
        status="processing"
    )
```

**Request/Response Models**:
```python
# anonyma_api/models/requests.py
from pydantic import BaseModel, Field, validator
from typing import Optional

class TextAnonymizationRequest(BaseModel):
    text: str = Field(..., description="Text to anonymize", max_length=10_000_000)
    mode: AnonymizationMode = Field(default=AnonymizationMode.REDACT)
    language: str = Field(default="it", pattern="^(it|en)$")
    use_ensemble: bool = Field(default=False)

    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v

class DocumentAnonymizationRequest(BaseModel):
    mode: AnonymizationMode = Field(default=AnonymizationMode.REDACT)
    language: str = Field(default="it")
    preserve_formatting: bool = Field(default=True)

# anonyma_api/models/responses.py
from typing import List, Dict, Optional
from datetime import datetime

class AnonymizationResponse(BaseModel):
    anonymized_text: str
    detections: List[Dict[str, Any]]
    mode: str
    processing_time: float
    detection_count: int

class DocumentJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    progress: Optional[float] = None
    result_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
```

##### 3.2 Async Processing with Celery
**Effort**: 3 days | **New File**: `anonyma_api/tasks.py`

**Dependencies**: `celery`, `redis`, `kombu`

- [ ] Set up Celery with Redis broker
- [ ] Create async tasks for document processing
- [ ] Implement progress tracking
- [ ] Add result backend for job status
- [ ] Configure task timeouts and retries
- [ ] Add monitoring dashboard

**Celery Configuration**:
```python
# anonyma_api/celery_app.py
from celery import Celery

celery_app = Celery(
    'anonyma',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
    task_soft_time_limit=3300,  # 55 min soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100
)

# anonyma_api/tasks.py
from celery import Task
from anonyma_core.documents.pipeline import DocumentPipeline
from anonyma_core import AnonymaEngine

@celery_app.task(bind=True, max_retries=3)
def process_document_async(
    self: Task,
    job_id: str,
    file_path: str,
    mode: str,
    batch_id: Optional[str] = None
):
    """Async document processing task"""
    try:
        # Update job status
        update_job_status(job_id, "processing", progress=0)

        # Initialize pipeline
        engine = AnonymaEngine(use_ensemble=False)
        pipeline = DocumentPipeline(engine)

        # Process document
        output_path = f"/tmp/results/{job_id}_anonymized"
        result = pipeline.process(
            file_path=Path(file_path),
            mode=AnonymizationMode[mode],
            output_path=Path(output_path)
        )

        # Update job as completed
        update_job_status(
            job_id,
            "completed",
            progress=100,
            output_path=output_path,
            detections=result.detections
        )

        return {"job_id": job_id, "status": "completed"}

    except Exception as e:
        logger.exception(f"Task failed for job {job_id}")
        update_job_status(job_id, "failed", error=str(e))
        raise self.retry(exc=e, countdown=60)
```

##### 3.3 Authentication & Authorization
**Effort**: 2 days | **New Module**: `anonyma_api/middleware/auth.py`

**Dependencies**: `python-jose`, `passlib`, `python-multipart`

- [ ] Implement JWT authentication
- [ ] Add API key support
- [ ] Create user management
- [ ] Implement role-based access control (RBAC)
- [ ] Add OAuth2 support

**Auth Implementation**:
```python
# anonyma_api/middleware/auth.py
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> User:
    """Validate JWT token and return user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return get_user_from_db(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Apply to endpoints
@app.post("/v1/anonymize/text")
async def anonymize_text(
    request: TextAnonymizationRequest,
    current_user: User = Depends(get_current_user)
):
    # Only authenticated users can access
    pass
```

##### 3.4 Rate Limiting
**Effort**: 1 day | **New Module**: `anonyma_api/middleware/rate_limit.py`

**Dependencies**: `slowapi`

- [ ] Implement rate limiting per user/IP
- [ ] Add tiered rate limits (free/paid)
- [ ] Create rate limit headers
- [ ] Add quota management

**Rate Limiting**:
```python
# anonyma_api/middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/v1/anonymize/text")
@limiter.limit("100/hour")  # 100 requests per hour
async def anonymize_text(request: Request, ...):
    pass
```

##### 3.5 API Documentation
**Effort**: 1 day

- [ ] Write comprehensive API documentation
- [ ] Add example requests/responses
- [ ] Create Postman collection
- [ ] Add authentication examples
- [ ] Document error codes

#### Success Metrics
- ✅ API response time <2s for text
- ✅ API response time <10s for small documents
- ✅ 99.9% API uptime
- ✅ Comprehensive OpenAPI spec
- ✅ Authentication working

#### Dependencies to Add
```txt
# requirements/api.txt
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
celery>=5.3.0
redis>=5.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
slowapi>=0.1.9
pydantic-settings>=2.0.0
```

---

### **PHASE 4: Security & Compliance**
**Timeline**: Weeks 11-12 | **Status**: 🔴 Not Started | **Priority**: 🔥 CRITICAL

#### Objectives
- Eliminate data leakage risks
- Implement encryption for sensitive data
- Add comprehensive audit trail
- Ensure GDPR compliance

#### Deliverables

##### 4.1 Encrypted Mappings
**Effort**: 2 days | **New Module**: `anonyma_core/security/crypto.py`

**Dependencies**: `cryptography`, `pycryptodome`

- [ ] Implement Fernet encryption for mappings
- [ ] Add key management system
- [ ] Encrypt data at rest
- [ ] Implement secure key rotation
- [ ] Add mapping expiration

**Implementation**:
```python
# anonyma_core/security/crypto.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import secrets
import json
from typing import Dict

class SecureMapping:
    """Encrypted mapping storage"""

    def __init__(self, master_key: bytes = None):
        self.master_key = master_key or Fernet.generate_key()
        self.fernet = Fernet(self.master_key)

    def encrypt_mapping(self, mapping: Dict[str, str]) -> tuple[bytes, str]:
        """
        Encrypt mapping dictionary

        Returns:
            encrypted_data: Encrypted mapping
            mapping_id: Unique ID for this mapping
        """
        mapping_id = secrets.token_urlsafe(32)
        json_data = json.dumps(mapping)
        encrypted = self.fernet.encrypt(json_data.encode())
        return encrypted, mapping_id

    def decrypt_mapping(self, encrypted_data: bytes, mapping_id: str) -> Dict[str, str]:
        """Decrypt mapping with ID verification"""
        decrypted = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())

    def secure_delete(self, data: bytes):
        """Securely delete sensitive data from memory"""
        # Overwrite memory
        if isinstance(data, bytes):
            data = bytearray(data)
            for i in range(len(data)):
                data[i] = 0
```

##### 4.2 Audit Trail System
**Effort**: 2 days | **New Module**: `anonyma_core/audit/`

- [ ] Create audit log database schema
- [ ] Log all anonymization operations
- [ ] Track user actions and IP addresses
- [ ] Implement tamper-proof logging
- [ ] Add audit log export

**Audit Schema**:
```python
# anonyma_core/audit/logger.py
from sqlalchemy import Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(String(64), primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(64))
    action = Column(String(50))  # 'anonymize_text', 'anonymize_document'
    document_id = Column(String(64))
    mode = Column(String(20))
    detections_count = Column(Integer)
    language = Column(String(10))
    ip_address = Column(String(45))
    user_agent = Column(String(256))
    metadata = Column(JSON)
    hash = Column(String(64))  # Tamper detection

    def compute_hash(self) -> str:
        """Compute hash for tamper detection"""
        data = f"{self.id}{self.timestamp}{self.user_id}{self.action}".encode()
        return hashlib.sha256(data).hexdigest()

class AuditLogger:
    """Audit logging service"""

    def log_anonymization(
        self,
        user_id: str,
        action: str,
        document_id: str,
        mode: str,
        detections_count: int,
        metadata: dict
    ):
        """Log anonymization operation"""
        log_entry = AuditLog(
            id=secrets.token_urlsafe(32),
            user_id=user_id,
            action=action,
            document_id=document_id,
            mode=mode,
            detections_count=detections_count,
            metadata=metadata
        )
        log_entry.hash = log_entry.compute_hash()

        session.add(log_entry)
        session.commit()

    def verify_integrity(self) -> bool:
        """Verify audit log has not been tampered"""
        logs = session.query(AuditLog).all()
        for log in logs:
            if log.hash != log.compute_hash():
                return False
        return True
```

##### 4.3 Input Sanitization & Validation
**Effort**: 2 days

- [ ] Validate all inputs with Pydantic
- [ ] Sanitize file names and paths
- [ ] Implement size limits
- [ ] Add malware scanning for uploads
- [ ] Rate limit file uploads

**Validation**:
```python
# anonyma_api/validators.py
from pydantic import BaseModel, validator, Field
import re

class SecureTextInput(BaseModel):
    text: str = Field(..., max_length=10_000_000)

    @validator('text')
    def sanitize_text(cls, v):
        # Remove potential injection attacks
        if re.search(r'<script|javascript:|onerror=', v, re.IGNORECASE):
            raise ValueError("Invalid text content")
        return v

def validate_file_upload(file: UploadFile):
    """Validate uploaded file"""
    # Check file size
    if file.size > 50_000_000:  # 50MB limit
        raise HTTPException(400, "File too large")

    # Check file type
    allowed_types = ['pdf', 'docx', 'xlsx', 'png', 'jpg']
    ext = file.filename.split('.')[-1].lower()
    if ext not in allowed_types:
        raise HTTPException(400, "File type not allowed")

    # Scan for malware (integrate with ClamAV)
    # scan_file_for_malware(file)
```

##### 4.4 GDPR Compliance Features
**Effort**: 3 days

- [ ] Implement data deletion (right to erasure)
- [ ] Add data export functionality (data portability)
- [ ] Create consent management system
- [ ] Implement data retention policies
- [ ] Add privacy policy acceptance

**GDPR Features**:
```python
# anonyma_core/compliance/gdpr.py

class GDPRCompliance:
    """GDPR compliance features"""

    def delete_user_data(self, user_id: str):
        """Right to erasure - delete all user data"""
        # Delete audit logs
        session.query(AuditLog).filter_by(user_id=user_id).delete()

        # Delete stored documents
        delete_user_documents(user_id)

        # Delete mappings
        delete_user_mappings(user_id)

        # Anonymize user record
        user = get_user(user_id)
        user.email = f"deleted_{user_id}@anonymized.local"
        user.name = "[DELETED]"
        session.commit()

    def export_user_data(self, user_id: str) -> dict:
        """Data portability - export all user data"""
        return {
            "user": get_user(user_id).to_dict(),
            "audit_logs": [log.to_dict() for log in get_user_logs(user_id)],
            "documents": [doc.to_dict() for doc in get_user_documents(user_id)]
        }

    def apply_retention_policy(self):
        """Delete data older than retention period"""
        retention_days = 365
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        # Delete old audit logs
        session.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()

        # Delete old documents
        delete_old_documents(cutoff_date)
```

##### 4.5 Secrets Management
**Effort**: 1 day

- [ ] Use environment variables for secrets
- [ ] Integrate with HashiCorp Vault
- [ ] Implement key rotation
- [ ] Add secrets encryption

**Secrets Management**:
```python
# anonyma_core/security/secrets.py
import os
from typing import Optional
import hvac  # HashiCorp Vault client

class SecretsManager:
    """Manage application secrets"""

    def __init__(self):
        self.vault_url = os.getenv("VAULT_URL")
        self.vault_token = os.getenv("VAULT_TOKEN")

        if self.vault_url:
            self.client = hvac.Client(url=self.vault_url, token=self.vault_token)

    def get_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault or environment"""
        # Try Vault first
        if self.client:
            try:
                secret = self.client.secrets.kv.v2.read_secret_version(path=key)
                return secret['data']['data']['value']
            except:
                pass

        # Fallback to environment variable
        return os.getenv(key)

    def set_secret(self, key: str, value: str):
        """Store secret in Vault"""
        if self.client:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=key,
                secret={'value': value}
            )
```

#### Success Metrics
- ✅ All sensitive data encrypted at rest
- ✅ Complete audit trail for all operations
- ✅ GDPR compliance verified
- ✅ Zero data leakage in logs
- ✅ Secrets never in source code

---

### **PHASE 5: Performance & Optimization**
**Timeline**: Weeks 13-14 | **Status**: 🔴 Not Started | **Priority**: 🟡 MEDIUM

#### Objectives
- Reduce model loading time
- Implement caching layer
- Add GPU support
- Optimize batch processing

#### Deliverables

##### 5.1 Model Optimization
**Effort**: 3 days | **New Module**: `anonyma_core/models/`

- [ ] Implement singleton pattern for model loading
- [ ] Add lazy loading
- [ ] Create model cache manager
- [ ] Implement model quantization
- [ ] Add GPU support

**Model Cache**:
```python
# anonyma_core/models/cache.py
from typing import Dict, Any
import torch
from threading import Lock

class ModelCache:
    """Singleton cache for ML models"""

    _instance = None
    _lock = Lock()
    _models: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def get_model(self, model_name: str, device: str = 'cpu'):
        """Get cached model or load it"""
        cache_key = f"{model_name}:{device}"

        if cache_key not in self._models:
            logger.info(f"Loading model {model_name} on {device}")
            model = self._load_model(model_name, device)
            self._models[cache_key] = model

        return self._models[cache_key]

    def _load_model(self, model_name: str, device: str):
        """Load model to device"""
        from flair.models import SequenceTagger
        model = SequenceTagger.load(model_name)

        if device == 'cuda' and torch.cuda.is_available():
            model = model.to(torch.device('cuda'))

        return model

    def clear_cache(self):
        """Clear model cache"""
        self._models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
```

**GPU Support**:
```python
# anonyma_core/detectors/flair_detector.py (optimized)
class FlairPIIDetectorOptimized(FlairPIIDetector):
    def __init__(self, use_gpu: bool = True):
        self.device = 'cuda' if use_gpu and torch.cuda.is_available() else 'cpu'
        self.model_cache = ModelCache()
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load models with caching"""
        for model_name in ['ner-multi', 'ner-english-ontonotes-fast']:
            self.models[model_name] = self.model_cache.get_model(
                model_name,
                self.device
            )

    def detect_batch(self, texts: List[str]) -> List[List[Detection]]:
        """Batch processing for efficiency"""
        sentences = [Sentence(text) for text in texts]

        with torch.no_grad():
            for model in self.models.values():
                # Process in batches
                model.predict(
                    sentences,
                    mini_batch_size=32,
                    embedding_storage_mode='none'
                )

        return [self._extract_entities(sent) for sent in sentences]
```

##### 5.2 Redis Caching Layer
**Effort**: 2 days | **New Module**: `anonyma_api/cache.py`

**Dependencies**: `redis`, `aiocache`

- [ ] Set up Redis connection
- [ ] Cache anonymization results
- [ ] Implement cache invalidation
- [ ] Add cache warming
- [ ] Monitor cache hit rate

**Cache Implementation**:
```python
# anonyma_api/cache.py
import hashlib
import json
from typing import Optional
import redis
from datetime import timedelta

class ResultCache:
    """Cache anonymization results"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour

    def _generate_key(self, text: str, mode: str, language: str) -> str:
        """Generate cache key from inputs"""
        data = f"{text}:{mode}:{language}"
        return f"anonyma:result:{hashlib.sha256(data.encode()).hexdigest()}"

    def get(self, text: str, mode: str, language: str) -> Optional[dict]:
        """Get cached result"""
        key = self._generate_key(text, mode, language)
        cached = self.redis.get(key)

        if cached:
            logger.debug("Cache hit", extra={"key": key})
            return json.loads(cached)

        logger.debug("Cache miss", extra={"key": key})
        return None

    def set(
        self,
        text: str,
        mode: str,
        language: str,
        result: dict,
        ttl: int = None
    ):
        """Cache result"""
        key = self._generate_key(text, mode, language)
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            json.dumps(result)
        )

    def invalidate_pattern(self, pattern: str):
        """Invalidate cache by pattern"""
        keys = self.redis.keys(f"anonyma:result:{pattern}*")
        if keys:
            self.redis.delete(*keys)
```

##### 5.3 Database Optimization
**Effort**: 2 days

- [ ] Add database indexes
- [ ] Implement connection pooling
- [ ] Add query optimization
- [ ] Use async SQLAlchemy

**Database Setup**:
```python
# anonyma_core/database/engine.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/anonyma",
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=False
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Add indexes
class AuditLog(Base):
    __tablename__ = 'audit_logs'

    # Add indexes for common queries
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )
```

##### 5.4 Batch Processing Optimization
**Effort**: 2 days

- [ ] Implement parallel processing
- [ ] Optimize I/O operations
- [ ] Add progress tracking
- [ ] Stream large files

**Optimized Batch Processing**:
```python
# anonyma_core/documents/pipeline.py
import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import List

class OptimizedPipeline(DocumentPipeline):
    def __init__(self, engine: AnonymaEngine, max_workers: int = 4):
        super().__init__(engine)
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    async def process_batch_parallel(
        self,
        file_paths: List[Path],
        mode: AnonymizationMode,
        output_dir: Path
    ) -> List[ProcessingResult]:
        """Process documents in parallel"""

        # Create tasks
        tasks = [
            self._process_single(file_path, mode, output_dir)
            for file_path in file_paths
        ]

        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return [r for r in results if not isinstance(r, Exception)]

    async def _process_single(
        self,
        file_path: Path,
        mode: AnonymizationMode,
        output_dir: Path
    ) -> ProcessingResult:
        """Process single document async"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.process,
            file_path,
            mode,
            output_dir / f"anonymized_{file_path.name}"
        )
```

#### Success Metrics
- ✅ Model load time <5s (cached)
- ✅ Cache hit rate >60%
- ✅ GPU processing 3-5x faster
- ✅ Batch processing 10x faster
- ✅ API p95 latency <3s

---

### **PHASE 6: Enterprise Features**
**Timeline**: Weeks 15-18 | **Status**: 🔴 Not Started | **Priority**: 🟢 LOW

#### Objectives
- Add multi-tenancy support
- Implement custom entity types
- Create analytics dashboard
- Add webhook notifications

#### Deliverables

##### 6.1 Multi-Tenancy
**Effort**: 5 days

- [ ] Implement tenant isolation
- [ ] Add per-tenant configuration
- [ ] Create tenant management API
- [ ] Implement resource quotas

##### 6.2 Custom Entity Types
**Effort**: 3 days

- [ ] Allow users to define custom patterns
- [ ] Create entity type management UI
- [ ] Implement regex validator
- [ ] Add entity type versioning

**Custom Entities**:
```python
# anonyma_core/detectors/custom_detector.py
class CustomEntityDetector(BaseDetector):
    """User-defined entity patterns"""

    def __init__(self, patterns: Dict[str, str]):
        self.patterns = patterns
        self._compile_patterns()

    def add_pattern(self, entity_type: str, pattern: str):
        """Add custom pattern"""
        # Validate regex
        try:
            re.compile(pattern)
        except re.error:
            raise ValueError(f"Invalid regex pattern: {pattern}")

        self.patterns[entity_type] = pattern
        self._compile_patterns()

# Usage
detector = CustomEntityDetector({
    "EMPLOYEE_ID": r"EMP-[0-9]{6}",
    "PROJECT_CODE": r"PRJ-[A-Z]{3}-[0-9]{4}",
    "INTERNAL_IP": r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
})
```

##### 6.3 Webhooks & Notifications
**Effort**: 2 days

- [ ] Implement webhook registration
- [ ] Add event triggers
- [ ] Create notification templates
- [ ] Add retry logic

**Webhooks**:
```python
# anonyma_api/webhooks.py
class WebhookManager:
    """Manage webhook notifications"""

    async def send_webhook(
        self,
        url: str,
        event: str,
        data: dict,
        max_retries: int = 3
    ):
        """Send webhook with retries"""
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url,
                        json={
                            "event": event,
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        timeout=10.0
                    )
                    response.raise_for_status()
                    return
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Webhook failed after {max_retries} attempts: {e}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

# Register webhook
@app.post("/v1/webhooks")
async def register_webhook(
    url: str,
    events: List[str],
    current_user: User = Depends(get_current_user)
):
    """Register webhook for events"""
    webhook = Webhook(
        url=url,
        events=events,
        user_id=current_user.id
    )
    session.add(webhook)
    session.commit()
    return {"webhook_id": webhook.id}
```

##### 6.4 Analytics Dashboard
**Effort**: 5 days

- [ ] Create metrics collection
- [ ] Implement dashboard backend
- [ ] Add data visualizations
- [ ] Create usage reports

**Analytics**:
```python
# anonyma_api/analytics.py
class AnalyticsService:
    """Collect and analyze usage metrics"""

    def get_usage_stats(self, user_id: str, days: int = 30) -> dict:
        """Get user usage statistics"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        logs = session.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= cutoff
        ).all()

        return {
            "total_requests": len(logs),
            "by_mode": self._count_by_mode(logs),
            "by_entity_type": self._count_by_entity_type(logs),
            "total_detections": sum(log.detections_count for log in logs),
            "avg_detections_per_request": np.mean([log.detections_count for log in logs]),
            "documents_processed": len([l for l in logs if 'document' in l.action])
        }

    def get_entity_distribution(self) -> dict:
        """Get distribution of detected entity types"""
        # Aggregate across all users
        pass
```

##### 6.5 Cost Tracking
**Effort**: 2 days

- [ ] Track API usage per user
- [ ] Calculate processing costs
- [ ] Implement billing integration
- [ ] Add usage alerts

#### Success Metrics
- ✅ Support for 100+ tenants
- ✅ Custom entities working
- ✅ Webhook delivery rate >99%
- ✅ Dashboard load time <2s

---

## 🚦 Implementation Priority Matrix

| Phase | Priority | Business Impact | Technical Effort | Risk |
|-------|----------|----------------|------------------|------|
| Phase 1: Foundation | 🔥 CRITICAL | High | Medium | Low |
| Phase 2: Documents | 🔥 CRITICAL | Very High | High | Medium |
| Phase 3: API | 🔥 HIGH | Very High | Medium | Low |
| Phase 4: Security | 🔥 CRITICAL | Very High | Medium | Medium |
| Phase 5: Performance | 🟡 MEDIUM | Medium | Medium | Low |
| Phase 6: Enterprise | 🟢 LOW | Medium | High | Low |

---

## 📊 Success Metrics & KPIs

### Technical Metrics
- **Test Coverage**: >80% across all modules
- **API Uptime**: >99.9%
- **API Latency**:
  - Text: p95 <2s
  - Documents: p95 <10s
- **Cache Hit Rate**: >60%
- **Error Rate**: <0.1%

### Business Metrics
- **Supported Formats**: 7+ (text, PDF, Word, Excel, PPT, images, email)
- **Detection Accuracy**: >95% for Italian PII
- **Processing Speed**:
  - Text: >100 requests/min
  - Documents: >10 documents/min
- **User Satisfaction**: >4.5/5

### Security Metrics
- **Zero Data Leakage**: No PII in logs or errors
- **Audit Coverage**: 100% of operations logged
- **GDPR Compliance**: Full compliance verified
- **Vulnerability Score**: 0 critical, 0 high

---

## 📦 Updated Tech Stack

### Core Processing (Existing)
- Flair (NER)
- Presidio (PII detection)
- PyTorch (ML framework)
- Faker (fake data generation)
- spaCy (NLP)

### Document Processing (New)
- **PDF**: pdfplumber, PyPDF2, reportlab, pdf2image
- **OCR**: pytesseract, easyocr, paddleocr
- **Office**: python-docx, openpyxl, python-pptx
- **Images**: Pillow, opencv-python
- **Email**: email-parser, flanker
- **Detection**: python-magic, filetype

### API & Services (New)
- **API**: FastAPI, uvicorn
- **Async**: celery, redis, kombu
- **Validation**: pydantic, pydantic-settings
- **Auth**: python-jose, passlib

### Storage & Database (New)
- **SQL**: sqlalchemy, alembic, asyncpg
- **NoSQL**: motor (MongoDB)
- **Object Storage**: boto3 (S3), azure-storage-blob
- **Cache**: redis, aiocache

### Security (New)
- **Encryption**: cryptography, pycryptodome
- **Secrets**: python-dotenv, hvac (Vault)
- **Scanning**: python-magic

### Monitoring (New)
- **Metrics**: prometheus-client
- **Tracing**: opentelemetry
- **Logging**: structlog, python-json-logger

### Development (New)
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Quality**: black, isort, mypy, ruff
- **Docs**: mkdocs, mkdocs-material

---

## 🎯 Quick Wins (Start Here!)

These can be implemented immediately with minimal effort:

### 1. Fix Logging (30 minutes)
Replace all `print()` statements with proper logging:
```python
import logging
logger = logging.getLogger(__name__)

# Before: print("🎭 Initializing...")
# After: logger.info("Initializing Anonyma Engine")
```

### 2. Add Configuration (1 hour)
Create `config/config.yaml`:
```yaml
detection:
  confidence_threshold: 0.7
  use_ensemble: false

models:
  flair:
    models: ["ner-multi"]
    cache_dir: ".flair_cache"

anonymization:
  default_mode: "redact"
  redaction_char: "█"
```

### 3. Basic Tests (2 hours)
Create `tests/unit/test_engine.py`:
```python
def test_anonymize_email():
    engine = AnonymaEngine(use_ensemble=False)
    text = "Contact: test@example.com"
    result = engine.anonymize(text, AnonymizationMode.REDACT)
    assert "@" not in result.anonymized_text
```

### 4. Simple API (3 hours)
Create `api/main.py`:
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/anonymize")
def anonymize(text: str, mode: str = "redact"):
    engine = AnonymaEngine()
    result = engine.anonymize(text, AnonymizationMode[mode.upper()])
    return {"anonymized": result.anonymized_text}
```

Run with: `uvicorn api.main:app --reload`

---

## 🔄 Recommended Implementation Strategy

### Option A: Foundation First (RECOMMENDED)
Best for long-term maintainability and quality.

**Week 1-3:**
1. Fix logging system
2. Add comprehensive tests
3. Implement configuration
4. Security hardening

**Week 4-7:**
5. Document support (PDF, images, Word)

**Week 8-10:**
6. REST API and async processing

**Pros**: Solid foundation, easier to debug, production-ready
**Cons**: Slower time to market

### Option B: Feature First
Best for quick MVP and market validation.

**Week 1-2:**
1. Basic PDF support

**Week 2-3:**
2. Simple REST API

**Week 3-4:**
3. Deploy MVP

**Week 5+:**
4. Add quality improvements

**Pros**: Fast time to market, early user feedback
**Cons**: Technical debt, harder to scale

### Option C: Hybrid (BALANCED)
Best balance of quality and speed.

**Week 1:**
1. Fix logging + basic tests

**Week 2-4:**
2. PDF support + simple API

**Week 5-6:**
3. Security hardening

**Week 7-10:**
4. More document formats

**Week 11-12:**
5. Performance optimization

**Pros**: Balanced approach, manageable risk
**Cons**: Requires discipline to not skip quality work

---

## 📝 Next Steps

1. **Review this roadmap** and prioritize phases based on business needs
2. **Choose implementation strategy** (A, B, or C)
3. **Set up development environment** with all necessary tools
4. **Create project board** (GitHub Projects, Jira) to track progress
5. **Start with Quick Wins** to build momentum
6. **Begin Phase 1** (Foundation) or Phase 2 (Documents) based on strategy

---

## 📚 Additional Resources

### Documentation to Create
- [ ] API Documentation (OpenAPI/Swagger)
- [ ] User Guide
- [ ] Developer Guide
- [ ] Deployment Guide
- [ ] Security Guide
- [ ] Troubleshooting Guide

### Infrastructure to Set Up
- [ ] CI/CD Pipeline (GitHub Actions, GitLab CI)
- [ ] Container Registry (Docker Hub, ECR)
- [ ] Kubernetes Cluster (if scaling needed)
- [ ] Monitoring Stack (Prometheus + Grafana)
- [ ] Log Aggregation (ELK Stack, Loki)

### Team Considerations
- **Backend Developer**: API, database, business logic
- **ML Engineer**: Model optimization, accuracy improvements
- **Frontend Developer**: Dashboard, admin panel (if needed)
- **DevOps Engineer**: Deployment, scaling, monitoring
- **Security Engineer**: Security audit, penetration testing
- **QA Engineer**: Test automation, quality assurance

---

## 🏁 Conclusion

This roadmap transforms Anonyma from a text-only proof-of-concept into a production-ready, enterprise-grade document anonymization platform. The journey spans approximately 12-18 weeks with a structured approach covering:

1. ✅ Solid foundation (logging, testing, config)
2. 📄 Multi-format document support (PDF, images, Office)
3. 🚀 Scalable API infrastructure
4. 🔒 Enterprise security and compliance
5. ⚡ Performance optimization
6. 🏢 Advanced enterprise features

**Current State**: Functional text anonymization tool
**Target State**: Production-ready document processing platform

The roadmap is flexible and can be adapted based on:
- Business priorities
- Resource availability
- Market feedback
- Technical constraints

**Remember**: Quality over speed. A well-built foundation will save countless hours of debugging and refactoring later.

---

*Document Version: 1.0*
*Last Updated: 2026-01-17*
*Status: Draft - Awaiting Review*
