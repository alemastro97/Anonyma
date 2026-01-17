FROM python:3.11-slim

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ita \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .
COPY ../requirements.txt ./parent_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy anonyma_core module
COPY ../anonyma_core /app/anonyma_core

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
