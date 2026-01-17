FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc g++ curl git && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy scripts for model download
COPY scripts/ scripts/

# Download models using script (più pulito)
RUN python scripts/download_models.py

# Copy source code
COPY . .

# Install package
RUN pip install -e .

# Default command - Start FastAPI server
CMD ["uvicorn", "anonyma_api.main:app", "--host", "0.0.0.0", "--port", "8000"]