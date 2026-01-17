# Phase 2: Document Processing Pipeline - COMPLETED ✅

## Overview

Phase 2 adds comprehensive document processing capabilities to Anonyma, enabling anonymization of PDFs, images, Word documents, Excel spreadsheets, and support for ANY custom sensitive data patterns.

**Status**: ✅ COMPLETE
**Started**: 2026-01-17
**Completed**: 2026-01-17
**Progress**: 100% (All core formats implemented)

---

## ✅ Completed Features

### 1. Document Architecture ✅

**Base Document System**:
- [documents/base.py](packages/anonyma_core/documents/base.py)
  - `BaseDocument` abstract class
  - `DocumentFormat` enum (PDF, Image, Word, Excel, etc.)
  - `DocumentMetadata` dataclass with comprehensive metadata
  - Clean interface for all document types

**Key Features**:
- Abstract methods: `extract_text()`, `rebuild()`, `_detect_format()`, `_extract_metadata()`
- Properties: `format`, `metadata`, `text_content` (cached)
- Methods: `get_text()`, `is_scanned()`, `get_metadata()`, `get_file_size()`

---

### 2. PDF Document Handler ✅

**Full PDF Support**:
- [documents/pdf_document.py](packages/anonyma_core/documents/pdf_document.py)
  - Digital PDF processing (with selectable text)
  - Scanned PDF processing (with OCR)
  - Multi-page support
  - Metadata extraction
  - PDF reconstruction with reportlab

**Features**:
- ✅ Text extraction from digital PDFs (via pdfplumber)
- ✅ OCR for scanned PDFs (via pytesseract + pdf2image)
- ✅ Automatic scanned/digital detection
- ✅ Multi-language OCR support (Italian + English)
- ✅ Metadata preservation (author, title, dates, page count)
- ✅ PDF reconstruction with anonymized content
- ✅ Proper resource cleanup

**Dependencies**:
```
pdfplumber>=0.10.0    # PDF text extraction
PyPDF2>=3.0.0         # PDF manipulation
reportlab>=4.0.0      # PDF generation
pdf2image>=1.16.0     # PDF to image conversion
pytesseract>=0.3.10   # OCR engine
```

---

### 3. Image Document Handler ✅

**Full Image Support with Visual Redaction**:
- [documents/image_document.py](packages/anonyma_core/documents/image_document.py)
  - OCR text extraction (EasyOCR and Tesseract)
  - Bounding box detection and mapping
  - Visual redaction (black boxes over sensitive text)
  - Support for PNG, JPG, JPEG, TIFF formats

**Features**:
- ✅ EasyOCR support for high-quality text recognition
- ✅ Tesseract OCR fallback
- ✅ Bounding box coordinate mapping
- ✅ Visual redaction with black rectangles
- ✅ Multi-language OCR (Italian + English)
- ✅ Image metadata extraction

**Dependencies**:
```
Pillow>=10.0.0        # Image processing
opencv-python>=4.8.0  # Computer vision
easyocr>=1.7.0        # Deep learning OCR
pytesseract>=0.3.10   # Traditional OCR
```

---

### 4. Word Document Handler ✅

**Full Word Support**:
- [documents/word_document.py](packages/anonyma_core/documents/word_document.py)
  - Text extraction from paragraphs
  - Table extraction and processing
  - Headers and footers extraction
  - Document reconstruction with structure preservation

**Features**:
- ✅ Paragraph-by-paragraph extraction
- ✅ Table data extraction
- ✅ Headers/footers handling
- ✅ Metadata extraction (author, title, dates)
- ✅ Document reconstruction with anonymized content
- ✅ Structure tracking for accurate rebuild

**Dependencies**:
```
python-docx>=1.0.0    # Word document processing
```

---

### 5. Excel Document Handler ✅

**Full Excel Support**:
- [documents/excel_document.py](packages/anonyma_core/documents/excel_document.py)
  - Multi-sheet support
  - Cell-by-cell data extraction
  - Spreadsheet reconstruction
  - Metadata extraction

**Features**:
- ✅ Multi-sheet processing
- ✅ Cell coordinate tracking
- ✅ Formula handling (converts to values)
- ✅ Metadata extraction
- ✅ Spreadsheet reconstruction with anonymized data
- ✅ Basic styling preservation

**Dependencies**:
```
openpyxl>=3.1.0       # Excel document processing
```

---

### 6. Custom Pattern Detector ✅

**CRITICAL FEATURE: Detect ANY Sensitive Data**:
- [detectors/custom_detector.py](packages/anonyma_core/detectors/custom_detector.py)
  - `CustomPattern` dataclass for ANY regex pattern
  - `CustomPatternDetector` for user-defined patterns
  - `CompoundPatternDetector` for chemical/research data
  - `InternalIDDetector` for company identifiers
  - Support for validation functions

**Features**:
- ✅ Regex-based pattern matching for ANY data type
- ✅ Not limited to standard PII (emails, names, etc.)
- ✅ Can detect: compound names, drug codes, internal IDs, etc.
- ✅ Optional validation functions for complex logic
- ✅ Pre-built pattern collections (compounds, IDs)
- ✅ High flexibility for domain-specific anonymization

**Example Patterns**:
```python
# Chemical compounds
detector.add_pattern("COMPOUND_ID", r"Compound-[A-Z]{3}-\d{3}")

# Internal IDs
detector.add_pattern("EMPLOYEE_ID", r"EMP-\d{6}")

# Lab data
detector.add_pattern("EXPERIMENT_ID", r"XP-\d{4}-\d{3}")

# With validation
detector.add_pattern("ORDER_ID", r"ORD-\d{5}", validate=validate_order)
```

---

### 7. Document Pipeline ✅

**Unified Processing Pipeline**:
- [documents/pipeline.py](packages/anonyma_core/documents/pipeline.py)
  - `DocumentPipeline` class
  - `ProcessingResult` dataclass
  - Automatic format detection
  - Complete workflow orchestration

**Registered Handlers**:
- ✅ PDF (digital and scanned)
- ✅ Images (PNG, JPG, TIFF)
- ✅ Word (.docx)
- ✅ Excel (.xlsx)

**Pipeline Steps**:
1. **Format Detection** - Detect document type from extension
2. **Handler Loading** - Load appropriate document handler
3. **Text Extraction** - Extract text (with OCR if needed)
4. **Anonymization** - Run PII detection and anonymization
5. **Reconstruction** - Rebuild document with anonymized content
6. **Output Saving** - Save anonymized document

**Example Usage**:
```python
from anonyma_core import AnonymaEngine
from anonyma_core.documents import DocumentPipeline
from anonyma_core.modes import AnonymizationMode

engine = AnonymaEngine(use_flair=False)
pipeline = DocumentPipeline(engine)

result = pipeline.process(
    file_path=Path("document.pdf"),
    mode=AnonymizationMode.REDACT,
    output_path=Path("anonymized.pdf")
)

print(f"Success: {result.success}")
print(f"Detections: {result.detections_count}")
print(f"Time: {result.processing_time:.2f}s")
```

---

### 8. Comprehensive Tests ✅

**Test Suites Created**:
- [tests/unit/test_documents.py](packages/tests/unit/test_documents.py)
  - Tests for all document handlers (PDF, Image, Word, Excel)
  - DocumentPipeline integration tests
  - ProcessingResult tests
  - Full workflow tests

- [tests/unit/test_custom_detector.py](packages/tests/unit/test_custom_detector.py)
  - CustomPattern tests
  - CustomPatternDetector tests
  - CompoundPatternDetector tests
  - InternalIDDetector tests
  - Pattern validation tests

**Test Coverage**:
- 50+ tests for document processing
- 40+ tests for custom pattern detection
- Integration tests for full workflows
- Mock-based tests for isolated unit testing

---

### 9. Example Scripts ✅

**Created Examples**:

1. **PDF Processing** - [examples/pdf_processing_example.py](packages/examples/pdf_processing_example.py)
   - Creates sample PDF with Italian PII
   - Processes with 3 anonymization modes
   - Shows metadata extraction
   - Demonstrates full pipeline

2. **Custom Patterns** - [examples/custom_patterns_example.py](packages/examples/custom_patterns_example.py)
   - Chemical compound detection
   - Internal ID detection
   - Lab experiment data
   - Pattern validation examples
   - 5 complete demonstrations

3. **Office Documents** - [examples/office_documents_example.py](packages/examples/office_documents_example.py)
   - Word document processing
   - Excel spreadsheet processing
   - Table handling
   - Multi-sheet processing
   - Structure preservation

**Run Examples**:
```bash
cd packages/examples
python pdf_processing_example.py
python custom_patterns_example.py
python office_documents_example.py
```

---

## 📊 Final Statistics

### Files Created (12)
1. `anonyma_core/documents/__init__.py` - Module exports
2. `anonyma_core/documents/base.py` - Base document system
3. `anonyma_core/documents/pdf_document.py` - PDF handler (374 lines)
4. `anonyma_core/documents/image_document.py` - Image handler (398 lines)
5. `anonyma_core/documents/word_document.py` - Word handler (321 lines)
6. `anonyma_core/documents/excel_document.py` - Excel handler (304 lines)
7. `anonyma_core/documents/pipeline.py` - Processing pipeline (341 lines)
8. `anonyma_core/detectors/custom_detector.py` - Custom patterns (400+ lines)
9. `tests/unit/test_documents.py` - Document tests (550+ lines)
10. `tests/unit/test_custom_detector.py` - Pattern tests (450+ lines)
11. `examples/pdf_processing_example.py` - PDF example (241 lines)
12. `examples/custom_patterns_example.py` - Custom patterns example (400 lines)
13. `examples/office_documents_example.py` - Office example (350+ lines)

### Dependencies Added (10)
```
# Document processing
pdfplumber>=0.10.0
PyPDF2>=3.0.0
reportlab>=4.0.0

# OCR support
pdf2image>=1.16.0
pytesseract>=0.3.10
easyocr>=1.7.0

# Image processing
Pillow>=10.0.0
opencv-python>=4.8.0

# Office documents
python-docx>=1.0.0
openpyxl>=3.1.0
```

### Code Statistics
- **Total Lines Added**: ~3,500+
- **Classes**: 9 (BaseDocument, PDFDocument, ImageDocument, WordDocument, ExcelDocument, DocumentPipeline, ProcessingResult, CustomPatternDetector, CustomPattern)
- **Methods**: 80+
- **Tests**: 90+

---

## 🎯 Phase 2 Goals - ACHIEVED

### Priority 1: Core Document Types ✅ 100%
- [x] PDF (digital)
- [x] PDF (scanned with OCR)
- [x] Images (PNG, JPG, TIFF) with visual redaction
- [x] Word (.docx)
- [x] Excel (.xlsx)

### Priority 2: Flexibility ✅ 100%
- [x] Custom pattern detection for ANY sensitive data
- [x] Not limited to standard PII
- [x] Chemical compound detection
- [x] Internal ID detection
- [x] Validation functions for complex logic

### Priority 3: Testing & Documentation ✅ 100%
- [x] Comprehensive test suite (90+ tests)
- [x] Multiple example scripts
- [x] Full documentation
- [x] Usage examples

---

## 🔧 How to Use

### Prerequisites
```bash
# Install all dependencies
cd packages
pip install -r requirements.txt

# For OCR, also install Tesseract:
# macOS: brew install tesseract tesseract-lang
# Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-ita
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### Basic Usage - PDF
```python
from pathlib import Path
from anonyma_core import AnonymaEngine
from anonyma_core.documents import DocumentPipeline
from anonyma_core.modes import AnonymizationMode

# Initialize
engine = AnonymaEngine(use_flair=False)
pipeline = DocumentPipeline(engine)

# Process PDF
result = pipeline.process(
    file_path=Path("document.pdf"),
    mode=AnonymizationMode.REDACT,
    language="it"
)

print(f"Success: {result.success}")
print(f"Detections: {result.detections_count}")
```

### Custom Patterns - ANY Data Type
```python
from anonyma_core.detectors.custom_detector import CustomPatternDetector
from anonyma_core.modes import Redactor

# Create detector for drug research codes
detector = CustomPatternDetector()
detector.add_pattern(
    name="DRUG_CODE",
    pattern=r"DRC-[A-Z0-9]{6}",
    confidence=0.95,
    description="Drug research code"
)

# Detect in text
text = "Study DRC-A4F7B2 showed 85% efficacy."
detections = detector.detect(text)

# Anonymize
redactor = Redactor()
anonymized = redactor.anonymize(text, detections)
print(anonymized)  # "Study [DRUG_CODE] showed 85% efficacy."
```

### Word Documents
```python
result = pipeline.process(
    file_path=Path("document.docx"),
    mode=AnonymizationMode.SUBSTITUTE,
    language="it"
)
```

### Excel Spreadsheets
```python
result = pipeline.process(
    file_path=Path("data.xlsx"),
    mode=AnonymizationMode.REDACT,
    language="it"
)
```

### Images with Visual Redaction
```python
result = pipeline.process(
    file_path=Path("scan.png"),
    mode=AnonymizationMode.VISUAL_REDACT,
    language="it"
)
# Creates image with black boxes over detected PII
```

---

## 📝 Technical Architecture

### Document Processing Flow
```
User File (PDF/Word/Excel/Image)
    ↓
DocumentPipeline
    ↓
Format Detection
    ↓
Handler Selection (PDFDocument/WordDocument/etc.)
    ↓
Text Extraction (with OCR if needed)
    ↓
AnonymaEngine (PII + Custom Pattern Detection)
    ↓
Anonymization (REDACT/SUBSTITUTE/VISUAL_REDACT)
    ↓
Document Reconstruction
    ↓
Anonymized Output File
```

### Custom Pattern System
```
CustomPatternDetector
    ├── add_pattern(name, regex, validate?)
    ├── detect(text) → detections
    └── Pre-built Collections:
        ├── CompoundPatternDetector
        │   ├── Compound names
        │   ├── Drug codes
        │   └── CAS numbers
        └── InternalIDDetector
            ├── Project codes
            ├── Employee IDs
            ├── Document IDs
            └── Contract IDs
```

---

## 🐛 Known Limitations

1. **PDF Layout**: Current rebuild is text-only, complex layouts not preserved
2. **Large Files**: No streaming support, files load entirely in memory
3. **OCR Accuracy**: Depends on image quality
4. **Font Preservation**: Rebuilt documents use default fonts

These are acceptable limitations for Phase 2. Advanced features can be added in future phases.

---

## ✅ Success Criteria - ALL MET

- [x] PDF support (digital + scanned) ✅
- [x] Image support with OCR ✅
- [x] Visual redaction for images ✅
- [x] Word document support ✅
- [x] Excel document support ✅
- [x] Custom pattern detection for ANY data type ✅
- [x] Unified pipeline working for all formats ✅
- [x] Comprehensive tests (90+ tests) ✅
- [x] Example scripts for each format ✅
- [x] Full documentation ✅

**Final Progress**: 100% ✅

---

## 🚀 What's Next - Phase 3

Now that Phase 2 is complete, potential next steps:

### Phase 3 Options:
1. **Advanced Features**
   - PowerPoint (.pptx) support
   - Email (.eml, .msg) support
   - Better layout preservation
   - Batch processing
   - Parallel processing

2. **API Layer**
   - REST API for document processing
   - Web UI for document upload
   - Batch processing endpoint
   - Async task queue

3. **Enterprise Features**
   - Cloud storage integration (S3, Azure)
   - Audit logging
   - User authentication
   - Processing quotas

---

## 📚 Key Achievements

1. **Flexibility**: System can now detect ANY type of sensitive data, not just standard PII
2. **Multi-format**: Supports 4 major document formats (PDF, Images, Word, Excel)
3. **Visual Redaction**: Can draw black boxes over sensitive regions in images
4. **OCR**: Full OCR support for scanned documents
5. **Custom Patterns**: Drug codes, compound names, internal IDs, etc.
6. **Well Tested**: 90+ comprehensive tests
7. **Documented**: Complete examples and usage documentation
8. **Clean Architecture**: Abstract base classes, unified pipeline

---

*Last Updated: 2026-01-17*
*Status: ✅ COMPLETE*
*Next: Phase 3 Planning*
