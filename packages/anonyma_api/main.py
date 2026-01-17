"""
Main FastAPI application.

Provides REST API endpoints for:
- Text anonymization
- Document processing (PDF, Word, Excel, Images)
- Batch processing
- Health checks

Enterprise Features:
- Redis-backed job persistence
- API key authentication
- Rate limiting per client
- Configurable via environment variables
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query, Security, Depends
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import uuid

from anonyma_core import AnonymaEngine
from anonyma_core.modes import AnonymizationMode
from anonyma_core.documents import DocumentPipeline, DocumentFormat
from anonyma_core.exceptions import AnonymaException
from anonyma_core.logging_config import get_logger

# Import enterprise features
from .config import settings
from .redis_manager import redis_manager
from .auth import get_api_key, check_rate_limit_dependency

# Import routers
try:
    from .routers import auth as auth_router
    AUTH_ROUTER_AVAILABLE = True
except ImportError:
    AUTH_ROUTER_AVAILABLE = False
    logger.warning("Auth router not available")

logger = get_logger(__name__)

# ============================================================================
# FastAPI App Setup
# ============================================================================

app = FastAPI(
    title=settings.app_name,
    description="REST API for document and text anonymization with enterprise features",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.debug,
)

# CORS middleware for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
if AUTH_ROUTER_AVAILABLE:
    app.include_router(auth_router.router, prefix="/api", tags=["authentication"])
    logger.info("Auth router included")

# ============================================================================
# Global State
# ============================================================================

# Initialize engines (lazy loading)
_engine_cache: Dict[str, AnonymaEngine] = {}
_pipeline_cache: Dict[str, DocumentPipeline] = {}

# Temporary storage for processed files
TEMP_DIR = Path(settings.temp_dir)
TEMP_DIR.mkdir(exist_ok=True)

# Background job storage
# Uses Redis if enabled, otherwise falls back to in-memory storage
_jobs: Dict[str, Dict[str, Any]] = {}  # Fallback storage


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job from Redis or in-memory storage"""
    if redis_manager.is_enabled:
        return redis_manager.get_job(job_id)
    return _jobs.get(job_id)


def save_job(job_id: str, job_data: Dict[str, Any]) -> bool:
    """Save job to Redis or in-memory storage"""
    if redis_manager.is_enabled:
        return redis_manager.save_job(job_id, job_data)
    _jobs[job_id] = job_data
    return True


def update_job_status(job_id: str, status: str, progress: float = None, **kwargs) -> bool:
    """Update job status in Redis or in-memory storage"""
    if redis_manager.is_enabled:
        return redis_manager.update_job_status(job_id, status, progress, **kwargs)

    if job_id in _jobs:
        _jobs[job_id]["status"] = status
        if progress is not None:
            _jobs[job_id]["progress"] = progress
        _jobs[job_id].update(kwargs)
        return True
    return False


def get_engine(use_flair: bool = False) -> AnonymaEngine:
    """Get or create anonymization engine"""
    cache_key = f"flair_{use_flair}"
    if cache_key not in _engine_cache:
        logger.info(f"Initializing AnonymaEngine (use_flair={use_flair})")
        _engine_cache[cache_key] = AnonymaEngine(use_flair=use_flair)
    return _engine_cache[cache_key]


def get_pipeline(use_flair: bool = False) -> DocumentPipeline:
    """Get or create document pipeline"""
    cache_key = f"flair_{use_flair}"
    if cache_key not in _pipeline_cache:
        logger.info(f"Initializing DocumentPipeline (use_flair={use_flair})")
        engine = get_engine(use_flair)
        _pipeline_cache[cache_key] = DocumentPipeline(engine)
    return _pipeline_cache[cache_key]


# ============================================================================
# Request/Response Models
# ============================================================================

class AnonymizeTextRequest(BaseModel):
    """Request model for text anonymization"""
    text: str = Field(..., description="Text to anonymize", max_length=1_000_000)
    mode: str = Field(
        default="redact",
        description="Anonymization mode: redact, substitute, or visual_redact"
    )
    language: str = Field(default="it", description="Language code (it, en)")
    use_flair: bool = Field(default=False, description="Use Flair NER (slower but more accurate)")

    class Config:
        schema_extra = {
            "example": {
                "text": "Il sig. Mario Rossi (email: mario.rossi@example.com) abita a Milano.",
                "mode": "redact",
                "language": "it",
                "use_flair": False
            }
        }


class AnonymizeTextResponse(BaseModel):
    """Response model for text anonymization"""
    success: bool
    anonymized_text: str
    detections_count: int
    detections: List[Dict[str, Any]]
    processing_time: float
    error: Optional[str] = None


class ProcessDocumentResponse(BaseModel):
    """Response model for document processing"""
    success: bool
    job_id: str
    format: Optional[str] = None
    detections_count: int = 0
    processing_time: float = 0.0
    download_url: Optional[str] = None
    error: Optional[str] = None


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float  # 0.0 to 1.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    version: str
    timestamp: str
    engines_loaded: Dict[str, bool]


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve web UI"""
    ui_path = STATIC_DIR / "index.html"
    if ui_path.exists():
        return HTMLResponse(content=ui_path.read_text(), status_code=200)
    else:
        return {
            "name": "Anonyma API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health"
        }


@app.get("/api", response_model=Dict[str, str])
async def api_info():
    """API information endpoint"""
    return {
        "name": "Anonyma API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat(),
        engines_loaded={
            "basic": "flair_False" in _engine_cache,
            "flair": "flair_True" in _engine_cache,
        }
    )


@app.get("/api/config", response_model=Dict[str, Any])
async def get_config(api_key: str = Depends(get_api_key)):
    """
    Get API configuration (requires authentication if enabled).

    Shows enabled features and limits.
    """
    return {
        "features": {
            "redis_enabled": settings.redis_enabled,
            "auth_enabled": settings.auth_enabled,
            "rate_limit_enabled": settings.rate_limit_enabled,
        },
        "limits": {
            "max_file_size": settings.max_file_size,
            "rate_limit_requests": settings.rate_limit_requests if settings.rate_limit_enabled else None,
            "rate_limit_window": settings.rate_limit_window if settings.rate_limit_enabled else None,
        },
        "version": settings.app_version,
    }


@app.post("/anonymize/text", response_model=AnonymizeTextResponse)
async def anonymize_text(
    request: AnonymizeTextRequest,
    api_key: str = Depends(get_api_key),
    _rate_limit: None = Depends(check_rate_limit_dependency)
):
    """
    Anonymize plain text.

    Detects and anonymizes PII in text using specified mode.

    Requires authentication if ANONYMA_AUTH_ENABLED=true.
    Subject to rate limiting if ANONYMA_RATE_LIMIT_ENABLED=true.
    """
    try:
        start_time = datetime.now()

        # Validate mode
        try:
            mode = AnonymizationMode(request.mode.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {request.mode}. Must be: redact, substitute, or visual_redact"
            )

        # Get engine and anonymize
        engine = get_engine(use_flair=request.use_flair)
        result = engine.anonymize(
            text=request.text,
            mode=mode,
            language=request.language
        )

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Get detections
        detections = []
        if hasattr(result, 'detections'):
            detections = result.detections

        logger.info(
            f"Text anonymized successfully",
            extra={
                "extra_fields": {
                    "mode": request.mode,
                    "detections": len(detections),
                    "processing_time": processing_time
                }
            }
        )

        return AnonymizeTextResponse(
            success=True,
            anonymized_text=result.anonymized_text,
            detections_count=len(detections),
            detections=detections,
            processing_time=processing_time
        )

    except AnonymaException as e:
        logger.error(f"Anonymization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post("/anonymize/document", response_model=ProcessDocumentResponse)
async def anonymize_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Query(default="redact", description="Anonymization mode"),
    language: str = Query(default="it", description="Language code"),
    use_flair: bool = Query(default=False, description="Use Flair NER"),
    api_key: str = Depends(get_api_key),
    _rate_limit: None = Depends(check_rate_limit_dependency)
):
    """
    Anonymize a document (PDF, Word, Excel, Image).

    Returns immediately with job_id. Use /jobs/{job_id} to check status.

    Requires authentication if ANONYMA_AUTH_ENABLED=true.
    Subject to rate limiting if ANONYMA_RATE_LIMIT_ENABLED=true.
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())

        # Save uploaded file
        upload_dir = TEMP_DIR / job_id
        upload_dir.mkdir(exist_ok=True)

        input_path = upload_dir / file.filename

        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(
            f"Document uploaded",
            extra={"extra_fields": {"job_id": job_id, "filename": file.filename, "size": len(content)}}
        )

        # Validate mode
        try:
            anonymization_mode = AnonymizationMode(mode.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {mode}"
            )

        # Initialize job status
        save_job(job_id, {
            "status": "pending",
            "progress": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "filename": file.filename,
        })

        # Schedule background processing
        background_tasks.add_task(
            process_document_background,
            job_id=job_id,
            input_path=input_path,
            mode=anonymization_mode,
            language=language,
            use_flair=use_flair
        )

        return ProcessDocumentResponse(
            success=True,
            job_id=job_id,
            detections_count=0,
            processing_time=0.0,
            download_url=f"/jobs/{job_id}/download"
        )

    except Exception as e:
        logger.error(f"Document upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Get status of a document processing job.

    Requires authentication if ANONYMA_AUTH_ENABLED=true.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        result=job.get("result"),
        error=job.get("error")
    )


@app.get("/jobs/{job_id}/download")
async def download_result(
    job_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Download anonymized document.

    Requires authentication if ANONYMA_AUTH_ENABLED=true.
    """
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed. Status: {job['status']}"
        )

    output_path = Path(job["result"]["output_file"])

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=output_path,
        filename=output_path.name,
        media_type="application/octet-stream"
    )


@app.get("/formats", response_model=List[str])
async def get_supported_formats():
    """
    Get list of supported document formats.
    """
    return [fmt.value for fmt in DocumentFormat]


# ============================================================================
# Background Tasks
# ============================================================================

async def process_document_background(
    job_id: str,
    input_path: Path,
    mode: AnonymizationMode,
    language: str,
    use_flair: bool
):
    """
    Process document in background.
    """
    try:
        # Update status
        update_job_status(job_id, "processing", progress=0.1)

        start_time = datetime.now()

        # Get pipeline
        pipeline = get_pipeline(use_flair=use_flair)

        # Generate output path
        output_filename = f"anonymized_{input_path.name}"
        output_path = input_path.parent / output_filename

        # Process document
        update_job_status(job_id, "processing", progress=0.3)

        result = pipeline.process(
            file_path=input_path,
            mode=mode,
            output_path=output_path,
            language=language,
            save_output=True
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        if result.success:
            update_job_status(
                job_id,
                "completed",
                progress=1.0,
                result={
                    "format": result.format.value if result.format else None,
                    "detections_count": result.detections_count,
                    "processing_time": processing_time,
                    "output_file": str(output_path),
                    "original_file": str(input_path),
                }
            )

            logger.info(
                f"Document processed successfully",
                extra={
                    "extra_fields": {
                        "job_id": job_id,
                        "detections": result.detections_count,
                        "processing_time": processing_time
                    }
                }
            )
        else:
            update_job_status(job_id, "failed", error=result.error)

            logger.error(
                f"Document processing failed",
                extra={"extra_fields": {"job_id": job_id, "error": result.error}}
            )

    except Exception as e:
        update_job_status(job_id, "failed", error=str(e))
        logger.error(f"Background processing error: {e}", exc_info=True)


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    logger.info("=" * 70)
    logger.info(f"Anonyma API v{settings.app_version} starting up")
    logger.info("=" * 70)
    logger.info(f"Temp directory: {TEMP_DIR}")
    logger.info(f"Redis enabled: {settings.redis_enabled}")
    if settings.redis_enabled:
        logger.info(f"Redis host: {settings.redis_host}:{settings.redis_port}")
        if redis_manager.is_enabled:
            logger.info("✓ Redis connection successful")
        else:
            logger.warning("✗ Redis connection failed - falling back to in-memory storage")
    logger.info(f"Authentication enabled: {settings.auth_enabled}")
    logger.info(f"Rate limiting enabled: {settings.rate_limit_enabled}")
    if settings.rate_limit_enabled:
        logger.info(f"Rate limit: {settings.rate_limit_requests} requests per {settings.rate_limit_window}s")
    logger.info("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources on shutdown"""
    logger.info("Anonyma API shutting down")

    # Close Redis connection
    if redis_manager.is_enabled:
        redis_manager.close()
        logger.info("Redis connection closed")

    # Cleanup temp files (optional - keep for download)
    # shutil.rmtree(TEMP_DIR, ignore_errors=True)


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
        workers=1 if settings.debug else settings.workers
    )
