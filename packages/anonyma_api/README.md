# Anonyma REST API

FastAPI-based REST API for document and text anonymization.

## Features

- **Text Anonymization** - Anonymize plain text with multiple modes
- **Document Processing** - Process PDF, Word, Excel, and Images
- **Async Processing** - Background jobs for large documents
- **Web UI** - Simple web interface for easy usage
- **OpenAPI Docs** - Auto-generated API documentation
- **Docker Support** - Easy deployment with Docker

## Quick Start

### Local Development

```bash
# Install dependencies
cd packages/anonyma_api
pip install -r requirements.txt

# Install Tesseract OCR (for document processing)
# macOS: brew install tesseract tesseract-lang
# Ubuntu: sudo apt-get install tesseract-ocr tesseract-ocr-ita
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

# Run server
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

Server will start on **http://localhost:8000**

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build manually
docker build -t anonyma-api .
docker run -p 8000:8000 anonyma-api
```

## API Endpoints

### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-17T10:30:00Z",
  "engines_loaded": {
    "basic": true,
    "flair": false
  }
}
```

### Text Anonymization

```bash
POST /anonymize/text
Content-Type: application/json

{
  "text": "Il sig. Mario Rossi (email: mario.rossi@example.com) abita a Milano.",
  "mode": "redact",
  "language": "it",
  "use_flair": false
}
```

Response:
```json
{
  "success": true,
  "anonymized_text": "Il sig. [PERSON] (email: [EMAIL]) abita a [LOCATION].",
  "detections_count": 3,
  "detections": [
    {
      "text": "Mario Rossi",
      "entity_type": "PERSON",
      "start": 8,
      "end": 19,
      "confidence": 0.95
    }
  ],
  "processing_time": 0.45
}
```

### Document Processing

```bash
POST /anonymize/document
Content-Type: multipart/form-data

file: document.pdf
mode: redact
language: it
use_flair: false
```

Response:
```json
{
  "success": true,
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "detections_count": 0,
  "processing_time": 0.0,
  "download_url": "/jobs/123e4567-e89b-12d3-a456-426614174000/download"
}
```

### Job Status

```bash
GET /jobs/{job_id}
```

Response:
```json
{
  "job_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "progress": 1.0,
  "result": {
    "format": "pdf",
    "detections_count": 15,
    "processing_time": 3.2,
    "output_file": "/tmp/anonyma_api/.../anonymized_document.pdf"
  }
}
```

### Download Result

```bash
GET /jobs/{job_id}/download
```

Returns the anonymized document file.

### Supported Formats

```bash
GET /formats
```

Response:
```json
["pdf", "image", "word", "excel", "text", "html"]
```

## Anonymization Modes

### 1. Redact (Default)
Replaces sensitive data with entity type markers:
- `Mario Rossi` → `[PERSON]`
- `mario.rossi@example.com` → `[EMAIL]`

### 2. Substitute
Replaces with fake but realistic data:
- `Mario Rossi` → `Giovanni Bianchi`
- `mario.rossi@example.com` → `andrea.verdi@example.it`

### 3. Visual Redact (Images Only)
Draws black boxes over sensitive regions in images.

## Supported Document Formats

- **PDF** - Digital and scanned (with OCR)
- **Word** - .docx files
- **Excel** - .xlsx files
- **Images** - PNG, JPG, JPEG, TIFF (with OCR)

## Web UI Usage

1. Open http://localhost:8000
2. Choose **Text Anonymization** or **Document Processing** tab
3. Enter text or upload document
4. Select anonymization mode and language
5. Click process button
6. View results and download (for documents)

## Python Client Example

```python
import requests

# Text anonymization
response = requests.post(
    "http://localhost:8000/anonymize/text",
    json={
        "text": "Mario Rossi vive a Milano",
        "mode": "redact",
        "language": "it"
    }
)
result = response.json()
print(result["anonymized_text"])

# Document processing
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/anonymize/document?mode=redact&language=it",
        files={"file": f}
    )

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/jobs/{job_id}").json()

# Download result when completed
if status["status"] == "completed":
    result_file = requests.get(f"http://localhost:8000/jobs/{job_id}/download")
    with open("anonymized.pdf", "wb") as f:
        f.write(result_file.content)
```

## cURL Examples

### Text Anonymization

```bash
curl -X POST "http://localhost:8000/anonymize/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mario Rossi abita a Milano",
    "mode": "redact",
    "language": "it"
  }'
```

### Document Upload

```bash
curl -X POST "http://localhost:8000/anonymize/document?mode=redact&language=it" \
  -F "file=@document.pdf"
```

### Check Job Status

```bash
curl "http://localhost:8000/jobs/{job_id}"
```

### Download Result

```bash
curl "http://localhost:8000/jobs/{job_id}/download" -o anonymized.pdf
```

## Configuration

### Environment Variables

- `PYTHONUNBUFFERED=1` - For Docker logging
- Custom temp directory can be configured in `main.py`

### Production Considerations

1. **CORS**: Update `allow_origins` in production
2. **Job Storage**: Use Redis instead of in-memory dict
3. **File Cleanup**: Implement periodic cleanup of temp files
4. **Rate Limiting**: Add rate limiting middleware
5. **Authentication**: Add API key or OAuth authentication
6. **HTTPS**: Use reverse proxy (nginx) with SSL

## Performance Tips

1. **Use `use_flair=false`** for faster processing (default)
2. **Enable `use_flair=true`** only when accuracy is critical
3. **Batch processing** for multiple documents (coming soon)
4. **Cache engines** by keeping server running

## Error Handling

All errors return standard JSON format:

```json
{
  "detail": "Error message here"
}
```

Common status codes:
- `200` - Success
- `400` - Invalid request (bad mode, missing file, etc.)
- `404` - Job not found
- `500` - Server error

## Development

### Project Structure

```
anonyma_api/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker image
├── docker-compose.yml  # Docker Compose config
├── static/
│   └── index.html      # Web UI
└── README.md           # This file
```

### Adding New Endpoints

1. Define request/response models with Pydantic
2. Add endpoint function with `@app.post()` or `@app.get()`
3. Document with docstrings
4. Test with `/docs` interactive UI

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests
pytest
```

## License

Same as Anonyma Core package.

## Support

- API Documentation: http://localhost:8000/docs
- Issues: https://github.com/yourusername/anonyma/issues
- Core Documentation: See `../README.md`
