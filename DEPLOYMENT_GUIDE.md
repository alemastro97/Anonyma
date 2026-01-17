# Anonyma API - Deployment Guide

Complete guide for deploying Anonyma API with enterprise features.

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Enterprise Features](#enterprise-features)
- [API Usage](#api-usage)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Install Dependencies

```bash
cd packages

# Install core dependencies
pip install -r requirements.txt

# Install API dependencies
pip install -r anonyma_api/requirements.txt
```

### 2. Basic Configuration

```bash
cd anonyma_api

# Copy example configuration
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Run the API

```bash
# Development mode (with auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- Web UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

---

## Development Setup

### Without Enterprise Features

Simplest setup for development:

```bash
cd packages/anonyma_api
python main.py
```

Default configuration:
- No authentication
- No rate limiting
- In-memory job storage
- Auto-reload enabled

### With Redis (Persistent Jobs)

```bash
# Start Redis
redis-server

# Configure Anonyma
export ANONYMA_REDIS_ENABLED=true
export ANONYMA_REDIS_HOST=localhost
export ANONYMA_REDIS_PORT=6379

# Run API
python main.py
```

### With Authentication

```bash
# Enable authentication
export ANONYMA_AUTH_ENABLED=true

# Generate secure master key
export ANONYMA_MASTER_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Run API
python main.py
```

Generate client API keys:

```python
from anonyma_api.auth import api_key_manager

# Generate key for a client
api_key = api_key_manager.generate_key(
    name="client-name",
    rate_limit=1000  # Custom rate limit for this key
)
print(f"API Key: {api_key}")
```

---

## Production Deployment

### 1. Install Production Dependencies

```bash
pip install -r requirements.txt
pip install -r anonyma_api/requirements.txt
pip install gunicorn  # For production server
```

### 2. Configure Environment

Create `.env` file:

```bash
# Application
ANONYMA_DEBUG=false
ANONYMA_WORKERS=8

# Redis (recommended for production)
ANONYMA_REDIS_ENABLED=true
ANONYMA_REDIS_HOST=redis.example.com
ANONYMA_REDIS_PORT=6379
ANONYMA_REDIS_PASSWORD=your_secure_password

# Authentication (required for production)
ANONYMA_AUTH_ENABLED=true
ANONYMA_MASTER_API_KEY=your_very_secure_master_key_here

# Rate Limiting (recommended)
ANONYMA_RATE_LIMIT_ENABLED=true
ANONYMA_RATE_LIMIT_REQUESTS=1000
ANONYMA_RATE_LIMIT_WINDOW=3600
```

### 3. Run with Gunicorn

```bash
gunicorn anonyma_api.main:app \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile -
```

### 4. Setup Systemd Service (Linux)

Create `/etc/systemd/system/anonyma-api.service`:

```ini
[Unit]
Description=Anonyma API Service
After=network.target redis.service

[Service]
Type=notify
User=anonyma
Group=anonyma
WorkingDirectory=/opt/anonyma/packages
Environment="PATH=/opt/anonyma/venv/bin"
EnvironmentFile=/opt/anonyma/packages/anonyma_api/.env
ExecStart=/opt/anonyma/venv/bin/gunicorn anonyma_api.main:app \
    --workers 8 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 300
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable anonyma-api
sudo systemctl start anonyma-api
sudo systemctl status anonyma-api
```

---

## Docker Deployment

### 1. Using Docker Compose (Recommended)

The repository includes a `docker-compose.yml`:

```bash
cd packages

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

Services included:
- `anonyma`: Main API service
- `redis`: Redis for job persistence and caching

### 2. Custom Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  anonyma:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      # Redis
      - ANONYMA_REDIS_ENABLED=true
      - ANONYMA_REDIS_HOST=redis
      - ANONYMA_REDIS_PORT=6379

      # Authentication
      - ANONYMA_AUTH_ENABLED=true
      - ANONYMA_MASTER_API_KEY=${ANONYMA_MASTER_API_KEY}

      # Rate Limiting
      - ANONYMA_RATE_LIMIT_ENABLED=true
      - ANONYMA_RATE_LIMIT_REQUESTS=1000
      - ANONYMA_RATE_LIMIT_WINDOW=3600

      # Performance
      - ANONYMA_WORKERS=8
      - ANONYMA_DEBUG=false

    depends_on:
      - redis
    restart: unless-stopped
    volumes:
      - anonyma_temp:/tmp/anonyma_api

volumes:
  redis_data:
  anonyma_temp:
```

### 3. Build and Run

```bash
# Set master API key
export ANONYMA_MASTER_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Build and start
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

---

## Configuration

### Environment Variables

All settings can be configured via environment variables with the `ANONYMA_` prefix.

#### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMA_APP_NAME` | Anonyma API | Application name |
| `ANONYMA_APP_VERSION` | 1.0.0 | API version |
| `ANONYMA_DEBUG` | false | Debug mode |

#### Server Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMA_HOST` | 0.0.0.0 | Server host |
| `ANONYMA_PORT` | 8000 | Server port |
| `ANONYMA_WORKERS` | 4 | Number of workers |

#### Redis Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMA_REDIS_ENABLED` | false | Enable Redis |
| `ANONYMA_REDIS_HOST` | localhost | Redis host |
| `ANONYMA_REDIS_PORT` | 6379 | Redis port |
| `ANONYMA_REDIS_PASSWORD` | None | Redis password |
| `ANONYMA_REDIS_DB` | 0 | Redis database |
| `ANONYMA_REDIS_JOB_TTL` | 86400 | Job TTL (seconds) |

#### Authentication Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMA_AUTH_ENABLED` | false | Enable authentication |
| `ANONYMA_API_KEY_HEADER` | X-API-Key | API key header name |
| `ANONYMA_MASTER_API_KEY` | None | Master API key |

#### Rate Limiting Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `ANONYMA_RATE_LIMIT_ENABLED` | false | Enable rate limiting |
| `ANONYMA_RATE_LIMIT_REQUESTS` | 100 | Requests per window |
| `ANONYMA_RATE_LIMIT_WINDOW` | 60 | Time window (seconds) |

---

## Enterprise Features

### Redis Integration

**Benefits**:
- Persistent job storage across API restarts
- Distributed deployment support
- Shared state across multiple workers
- Built-in caching layer

**Setup**:
```bash
# Install Redis
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
# Docker: docker run -d -p 6379:6379 redis:7-alpine

# Configure Anonyma
export ANONYMA_REDIS_ENABLED=true
export ANONYMA_REDIS_HOST=localhost
export ANONYMA_REDIS_PORT=6379
```

**Verify**:
```bash
curl http://localhost:8000/api/config
```

### Authentication

**Benefits**:
- Secure API access
- Client identification
- Per-client rate limits
- Usage tracking

**Setup**:
```bash
# Enable authentication
export ANONYMA_AUTH_ENABLED=true

# Generate master key
export ANONYMA_MASTER_API_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**Generate Client Keys**:
```python
from anonyma_api.auth import api_key_manager

# Standard key
key = api_key_manager.generate_key("client-1")

# With custom rate limit
key = api_key_manager.generate_key("client-2", rate_limit=5000)

# List all keys
keys = api_key_manager.list_keys()
```

**Using API Keys**:
```bash
# Make authenticated request
curl -X POST http://localhost:8000/anonymize/text \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Mario Rossi lives in Milan"}'
```

### Rate Limiting

**Benefits**:
- Prevent API abuse
- Fair resource allocation
- Cost control
- DDoS protection

**Setup**:
```bash
export ANONYMA_RATE_LIMIT_ENABLED=true
export ANONYMA_RATE_LIMIT_REQUESTS=100  # Requests per window
export ANONYMA_RATE_LIMIT_WINDOW=60     # Window in seconds
```

**Response Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

**Rate Limit Response (429)**:
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

---

## API Usage

### Text Anonymization

```bash
# Basic request
curl -X POST http://localhost:8000/anonymize/text \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mario Rossi (mario.rossi@email.com) lives in Milan",
    "mode": "redact",
    "language": "it"
  }'

# With authentication
curl -X POST http://localhost:8000/anonymize/text \
  -H "X-API-Key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Mario Rossi lives in Milan",
    "mode": "substitute"
  }'
```

### Document Anonymization

```bash
# Upload document
curl -X POST http://localhost:8000/anonymize/document \
  -H "X-API-Key: your_api_key" \
  -F "file=@document.pdf" \
  -F "mode=redact"

# Response
{
  "success": true,
  "job_id": "abc-123-def",
  "download_url": "/jobs/abc-123-def/download"
}

# Check status
curl http://localhost:8000/jobs/abc-123-def \
  -H "X-API-Key: your_api_key"

# Download result
curl http://localhost:8000/jobs/abc-123-def/download \
  -H "X-API-Key: your_api_key" \
  -o anonymized_document.pdf
```

### Supported Formats

```bash
curl http://localhost:8000/formats
```

Returns: `["pdf", "image", "word", "excel", "powerpoint", "email", "text"]`

---

## Troubleshooting

### Redis Connection Failed

**Symptom**: Warning in logs: "Redis connection failed - falling back to in-memory storage"

**Solutions**:
1. Check Redis is running: `redis-cli ping` (should return "PONG")
2. Verify host/port in configuration
3. Check firewall rules
4. Verify password if configured

### Authentication Issues

**Symptom**: 401 Unauthorized responses

**Solutions**:
1. Verify `ANONYMA_AUTH_ENABLED=true`
2. Check API key is being sent in `X-API-Key` header
3. Verify key with: `api_key_manager.validate_key(key)`
4. Regenerate key if needed

### Rate Limit Errors

**Symptom**: 429 Too Many Requests

**Solutions**:
1. Wait for rate limit window to reset (check `X-RateLimit-Reset` header)
2. Request higher rate limit for your API key
3. Distribute requests over longer time period
4. Consider increasing global limits in production

### Job Not Found

**Symptom**: 404 when checking job status

**Solutions**:
1. Check job_id is correct
2. Verify Redis connection if enabled (jobs stored in Redis)
3. Check job TTL hasn't expired (default 24 hours)
4. Ensure using same API instance (or Redis for shared state)

### Large File Upload Fails

**Solutions**:
1. Check `ANONYMA_MAX_FILE_SIZE` setting
2. Increase nginx/proxy timeout if using reverse proxy
3. Increase `ANONYMA_TEMP_FILE_TTL` if needed
4. Ensure sufficient disk space in temp directory

---

## Performance Optimization

### For High Load

```bash
# Increase workers
ANONYMA_WORKERS=16

# Enable Redis caching
ANONYMA_REDIS_ENABLED=true
ANONYMA_ENABLE_CACHING=true
ANONYMA_CACHE_TTL=3600

# Increase background workers
ANONYMA_BACKGROUND_WORKERS=8
```

### For Large Documents

```bash
# Increase max file size
ANONYMA_MAX_FILE_SIZE=524288000  # 500 MB

# Increase temp file TTL
ANONYMA_TEMP_FILE_TTL=172800  # 48 hours
```

### Monitoring

Check health endpoint regularly:
```bash
curl http://localhost:8000/health
```

Monitor Redis:
```bash
redis-cli INFO stats
redis-cli DBSIZE
```

---

## Security Best Practices

1. **Always enable authentication in production**:
   ```bash
   ANONYMA_AUTH_ENABLED=true
   ANONYMA_MASTER_API_KEY=<secure_random_key>
   ```

2. **Use strong API keys**:
   ```python
   # Generate strong keys
   import secrets
   secrets.token_urlsafe(32)
   ```

3. **Enable rate limiting**:
   ```bash
   ANONYMA_RATE_LIMIT_ENABLED=true
   ```

4. **Use HTTPS in production**:
   - Deploy behind nginx/Caddy with SSL
   - Use Let's Encrypt for free certificates

5. **Secure Redis**:
   - Use password authentication
   - Bind to localhost or private network
   - Use Redis ACLs if available

6. **Regular updates**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/your-repo/anonyma/issues
- Documentation: See `ENTERPRISE_FEATURES_COMPLETE.md`
- Examples: See `examples/` directory

---

**Last Updated**: 2026-01-17
**Version**: 1.0.0
