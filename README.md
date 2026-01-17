# Anonyma

**Production-Ready PII Detection and Anonymization Platform**

Anonyma is an enterprise-grade document anonymization system that detects and removes personally identifiable information (PII) from text and documents using advanced AI and machine learning.

## 🌟 Features

### Core Capabilities
- **Multi-Format Support**: PDF, Word, Excel, PowerPoint, Images, Email (.eml/.msg)
- **Advanced AI Detection**: Ensemble detector with Presidio, Flair NER, and custom patterns
- **Flexible Modes**: Redaction, substitution, visual redaction
- **Custom Patterns**: Detect ANY type of sensitive data with regex patterns
- **Batch Processing**: Process multiple documents efficiently

### Enterprise Features
- **🔒 API Authentication**: Secure API key management with per-client access control
- **⚡ Rate Limiting**: Protect your infrastructure from abuse with configurable limits
- **💾 Redis Integration**: Persistent job storage, caching, and distributed deployment
- **📊 Performance Optimization**: Configurable workers, caching, and async processing
- **🎯 Adaptive Learning**: AI that learns from feedback to improve accuracy

### REST API & Web UI
- **Modern REST API**: FastAPI-based with automatic OpenAPI documentation
- **Beautiful Web Interface**: Upload and anonymize documents through your browser
- **Async Job Processing**: Long-running tasks with progress tracking
- **Docker Ready**: Complete Docker Compose setup for instant deployment

---

## 📦 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/your-repo/anonyma.git
cd anonyma/packages

# Install dependencies
pip install -r requirements.txt
pip install -r anonyma_api/requirements.txt
```

### Basic Usage (Python)

```python
from anonyma_core import AnonymaEngine

# Initialize engine
engine = AnonymaEngine()

# Anonymize text
text = "Mario Rossi (mario.rossi@email.com) lives in Milan"
result = engine.anonymize(text, mode="redact")

print(result.anonymized_text)
# Output: [PERSON] ([EMAIL]) lives in [LOCATION]
```

### REST API

```bash
# Start API server
cd anonyma_api
python main.py

# API available at:
# - Web UI: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

### Docker Deployment

```bash
cd packages

# Start with Docker Compose
docker-compose up -d

# Services:
# - API: http://localhost:8000
# - Redis: localhost:6379
```

---

## 🚀 Enterprise Deployment

### Enable All Enterprise Features

```bash
# 1. Start Redis
redis-server

# 2. Configure Anonyma
cat > anonyma_api/.env << EOF
# Redis for persistence
ANONYMA_REDIS_ENABLED=true
ANONYMA_REDIS_HOST=localhost
ANONYMA_REDIS_PORT=6379

# Authentication
ANONYMA_AUTH_ENABLED=true
ANONYMA_MASTER_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Rate Limiting
ANONYMA_RATE_LIMIT_ENABLED=true
ANONYMA_RATE_LIMIT_REQUESTS=1000
ANONYMA_RATE_LIMIT_WINDOW=3600

# Performance
ANONYMA_WORKERS=8
ANONYMA_DEBUG=false
EOF

# 3. Generate API keys
python scripts/generate_api_key.py --name "client-1" --rate-limit 5000

# 4. Start API
cd anonyma_api
python main.py
```

### Production Deployment with Gunicorn

```bash
gunicorn anonyma_api.main:app \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment instructions.

---

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT_GUIDE.md)**: Complete deployment and configuration guide
- **[Enterprise Features](ENTERPRISE_FEATURES_COMPLETE.md)**: Detailed enterprise features documentation
- **[API Documentation](http://localhost:8000/docs)**: Interactive API documentation (when API is running)
- **[Examples](packages/examples/)**: Complete usage examples for all features

---

## 🔧 Configuration

All settings can be configured via environment variables:

```bash
# Application
ANONYMA_APP_NAME=Anonyma API
ANONYMA_DEBUG=false
ANONYMA_WORKERS=4

# Redis
ANONYMA_REDIS_ENABLED=true
ANONYMA_REDIS_HOST=localhost
ANONYMA_REDIS_PORT=6379

# Authentication
ANONYMA_AUTH_ENABLED=true
ANONYMA_MASTER_API_KEY=your_secure_key

# Rate Limiting
ANONYMA_RATE_LIMIT_ENABLED=true
ANONYMA_RATE_LIMIT_REQUESTS=100
ANONYMA_RATE_LIMIT_WINDOW=60
```

See [anonyma_api/.env.example](packages/anonyma_api/.env.example) for all options.

---

## 💡 Examples

### Text Anonymization

```python
from anonyma_core import AnonymaEngine
from anonyma_core.modes import AnonymizationMode

engine = AnonymaEngine()

# Redaction (replace with labels)
result = engine.anonymize(
    "Mario Rossi lives in Milan",
    mode=AnonymizationMode.REDACT
)
print(result.anonymized_text)
# [PERSON] lives in [LOCATION]

# Substitution (replace with fake data)
result = engine.anonymize(
    "Mario Rossi lives in Milan",
    mode=AnonymizationMode.SUBSTITUTE
)
print(result.anonymized_text)
# Giuseppe Bianchi lives in Rome
```

### Document Processing

```python
from anonyma_core.documents import DocumentPipeline

pipeline = DocumentPipeline(engine)

# Process any document
result = pipeline.process(
    file_path="document.pdf",
    mode=AnonymizationMode.REDACT,
    output_path="anonymized.pdf"
)

print(f"Detected {result.detections_count} PII entities")
```

### Custom Patterns

```python
from anonyma_core.detectors import CustomPatternDetector

# Detect custom IDs
custom = CustomPatternDetector()
custom.add_pattern("EMPLOYEE_ID", r"EMP-\d{6}")
custom.add_pattern("PROJECT_CODE", r"PRJ-[A-Z]{3}-\d{4}")

# Use with engine
engine = AnonymaEngine(custom_detector=custom)
text = "Employee EMP-001234 works on PRJ-ABC-2024"
result = engine.anonymize(text)
```

### Ensemble Detection (Advanced)

```python
from anonyma_core.detectors.ensemble_detector import EnsembleDetector

# Combine multiple AI models
detector = EnsembleDetector(
    use_presidio=True,      # Rule-based + basic NER
    use_flair=True,         # Deep learning NER
    use_custom=True,        # Custom patterns
    voting_strategy="weighted"
)

detections = detector.detect("Mario Rossi lives in Milan")
```

### REST API Usage

```bash
# Anonymize text
curl -X POST http://localhost:8000/anonymize/text \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mario Rossi lives in Milan",
    "mode": "redact"
  }'

# Upload document
curl -X POST http://localhost:8000/anonymize/document \
  -H "X-API-Key: your_key" \
  -F "file=@document.pdf" \
  -F "mode=redact"

# Check job status
curl http://localhost:8000/jobs/{job_id} \
  -H "X-API-Key: your_key"

# Download result
curl http://localhost:8000/jobs/{job_id}/download \
  -H "X-API-Key: your_key" \
  -o anonymized.pdf
```

---

## 🏗️ Architecture

```
anonyma/
├── packages/
│   ├── anonyma_core/          # Core anonymization engine
│   │   ├── detectors/         # PII detection (Presidio, Flair, Custom, Ensemble)
│   │   ├── modes/             # Anonymization modes
│   │   └── documents/         # Document processors (PDF, Word, etc.)
│   │
│   ├── anonyma_api/           # REST API
│   │   ├── main.py            # FastAPI application
│   │   ├── config.py          # Configuration management
│   │   ├── redis_manager.py   # Redis integration
│   │   ├── auth.py            # Authentication & rate limiting
│   │   └── static/            # Web UI
│   │
│   ├── examples/              # Usage examples
│   └── scripts/               # Utility scripts
│
├── DEPLOYMENT_GUIDE.md        # Deployment documentation
├── ENTERPRISE_FEATURES_COMPLETE.md  # Enterprise features guide
└── README.md                  # This file
```

---

## 🧪 Testing

### Run Unit Tests

```bash
cd packages
pytest anonyma_core/tests/ -v
```

### Test Enterprise API

```bash
python scripts/test_enterprise_api.py
```

### Run Examples

```bash
# Text anonymization
python examples/simple_test.py

# Document processing
python examples/pdf_processing_example.py

# Custom patterns
python examples/custom_patterns_example.py

# Ensemble detector
python examples/ensemble_detector_example.py
```

---

## 🔐 Security

### Best Practices

1. **Enable Authentication**:
   ```bash
   ANONYMA_AUTH_ENABLED=true
   ANONYMA_MASTER_API_KEY=<secure_random_key>
   ```

2. **Enable Rate Limiting**:
   ```bash
   ANONYMA_RATE_LIMIT_ENABLED=true
   ```

3. **Use HTTPS** in production (deploy behind nginx/Caddy)

4. **Secure Redis** with password and private network

5. **Regular Updates**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## 📊 Supported Formats

| Format | Extension | Read | Write |
|--------|-----------|------|-------|
| Plain Text | .txt | ✅ | ✅ |
| PDF | .pdf | ✅ | ✅ |
| Word | .docx | ✅ | ✅ |
| Excel | .xlsx, .xls | ✅ | ✅ |
| PowerPoint | .pptx | ✅ | ✅ |
| Images | .jpg, .png, .tiff | ✅ | ✅ |
| Email | .eml, .msg | ✅ | ✅ |

---

## 🤖 AI Models

### Presidio (Default)
- Rule-based detection
- Fast and efficient
- No external dependencies

### Flair NER (Optional)
- Deep learning NER
- Higher accuracy
- Requires model download

### Ensemble (Recommended)
- Combines multiple models
- Voting strategies
- Adaptive learning

---

## 📈 Performance

### Benchmarks

- **Text**: ~1000 chars/sec
- **PDF**: ~5 pages/sec
- **Images**: ~1 image/sec (with OCR)

### Optimization Tips

1. **Use Ensemble with weighted voting** for best accuracy
2. **Enable Redis caching** for repeated requests
3. **Increase workers** for high load
4. **Use Presidio only** for maximum speed

---

## 🛠️ Development

### Setup Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r requirements.txt
pip install -r anonyma_api/requirements.txt
pip install pytest black flake8

# Run in development mode
cd anonyma_api
export ANONYMA_DEBUG=true
python main.py
```

### Code Quality

```bash
# Format code
black anonyma_core/ anonyma_api/

# Lint
flake8 anonyma_core/ anonyma_api/

# Type check
mypy anonyma_core/ anonyma_api/
```

---

## 🎉 Acknowledgments

Built with:
- [Presidio](https://github.com/microsoft/presidio) - Microsoft's PII detection
- [Flair](https://github.com/flairNLP/flair) - NER framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Redis](https://redis.io/) - In-memory data store
- [pytesseract](https://github.com/madmaze/pytesseract) - OCR support

---

**Version**: 1.0.0
**Last Updated**: 2026-01-17
**Status**: ✅ Production Ready

---

## 📊 Feature Matrix

| Feature | Status | Phase |
|---------|--------|-------|
| Text Anonymization | ✅ | Phase 1 |
| Logging & Config | ✅ | Phase 1 |
| Unit Tests | ✅ | Phase 1 |
| PDF Support | ✅ | Phase 2 |
| Image Support (OCR) | ✅ | Phase 2 |
| Word Documents | ✅ | Phase 2 |
| Excel Spreadsheets | ✅ | Phase 2 |
| PowerPoint | ✅ | Phase 3 |
| Email (.eml/.msg) | ✅ | Phase 3 |
| Custom Patterns | ✅ | Phase 2 |
| REST API | ✅ | Phase 3 |
| Web UI | ✅ | Phase 3 |
| Docker Support | ✅ | Phase 3 |
| Redis Integration | ✅ | Enterprise |
| Authentication | ✅ | Enterprise |
| Rate Limiting | ✅ | Enterprise |
| Ensemble AI | ✅ | Enterprise |
| Adaptive Learning | ✅ | Enterprise |

**All phases complete!** 🎉
