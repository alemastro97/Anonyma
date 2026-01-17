"""
API Configuration.

Configuration for Anonyma API including:
- Redis settings
- Authentication
- Rate limiting
- Performance tuning
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """API Configuration Settings"""

    # Application
    app_name: str = "Anonyma API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1

    # Redis Configuration
    redis_enabled: bool = False
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_job_ttl: int = 86400  # 24 hours

    # Authentication
    auth_enabled: bool = False
    api_key_header: str = "X-API-Key"
    master_api_key: Optional[str] = None  # For admin access

    # Rate Limiting
    rate_limit_enabled: bool = False
    rate_limit_requests: int = 100  # requests per window
    rate_limit_window: int = 60  # seconds

    # File Processing
    max_file_size: int = 100 * 1024 * 1024  # 100 MB
    temp_dir: str = "/tmp/anonyma_api"
    temp_file_ttl: int = 3600  # 1 hour

    # Performance
    background_workers: int = 2
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes

    # CORS
    cors_origins: list = ["*"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_prefix = "ANONYMA_"
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
