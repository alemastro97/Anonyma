"""
API Authentication and Authorization.

Provides:
- API key authentication
- Rate limiting
- Access control
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from typing import Optional
import hashlib
import secrets

from .config import settings
from .redis_manager import redis_manager
from anonyma_core.logging_config import get_logger

logger = get_logger(__name__)

# API Key header
api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)


class APIKeyManager:
    """
    Manages API keys and authentication.

    Features:
    - API key validation
    - Key generation
    - Access tracking
    """

    def __init__(self):
        """Initialize API key manager"""
        self._keys: dict = {}  # In-memory store (would use DB in production)

        # Load master key if configured
        if settings.master_api_key:
            self._keys[settings.master_api_key] = {
                "name": "Master Key",
                "is_master": True,
                "rate_limit": 10000,  # Higher limit for master
            }

    def generate_key(self, name: str = "default", rate_limit: int = None) -> str:
        """
        Generate a new API key.

        Args:
            name: Key name/description
            rate_limit: Custom rate limit (default from settings)

        Returns:
            Generated API key
        """
        # Generate secure random key
        key = f"ak_{secrets.token_urlsafe(32)}"

        # Store key metadata
        self._keys[key] = {
            "name": name,
            "is_master": False,
            "rate_limit": rate_limit or settings.rate_limit_requests,
            "created_at": __import__('datetime').datetime.utcnow().isoformat(),
        }

        logger.info(f"Generated API key: {name}")
        return key

    def validate_key(self, api_key: str) -> Optional[dict]:
        """
        Validate API key.

        Args:
            api_key: API key to validate

        Returns:
            Key metadata if valid, None otherwise
        """
        return self._keys.get(api_key)

    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke API key.

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked successfully
        """
        if api_key in self._keys:
            del self._keys[api_key]
            logger.info(f"API key revoked: {api_key[:10]}...")
            return True
        return False

    def list_keys(self) -> list:
        """
        List all API keys.

        Returns:
            List of key metadata (without actual keys)
        """
        return [
            {
                "key_prefix": key[:10] + "...",
                **metadata
            }
            for key, metadata in self._keys.items()
        ]


# Global API key manager
api_key_manager = APIKeyManager()


# ============================================================================
# Authentication Dependency
# ============================================================================

async def get_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Dependency for API key authentication.

    Args:
        api_key: API key from header

    Returns:
        Validated API key

    Raises:
        HTTPException: If authentication fails
    """
    # Skip if authentication disabled
    if not settings.auth_enabled:
        return "no-auth"

    # Check if key provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate key
    key_info = api_key_manager.validate_key(api_key)
    if not key_info:
        logger.warning(f"Invalid API key attempt: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    logger.debug(f"Authenticated: {key_info['name']}")
    return api_key


# ============================================================================
# Rate Limiting
# ============================================================================

class RateLimiter:
    """
    Rate limiting for API requests.

    Features:
    - Per-client limits
    - Configurable windows
    - Redis-backed (if enabled)
    """

    def __init__(self):
        """Initialize rate limiter"""
        self._enabled = settings.rate_limit_enabled
        self._requests = settings.rate_limit_requests
        self._window = settings.rate_limit_window

    async def check_rate_limit(self, client_id: str, custom_limit: int = None) -> tuple[bool, int]:
        """
        Check if client is within rate limit.

        Args:
            client_id: Client identifier (API key or IP)
            custom_limit: Custom limit override

        Returns:
            (allowed, remaining) tuple

        Raises:
            HTTPException: If rate limit exceeded
        """
        if not self._enabled:
            return True, self._requests

        limit = custom_limit or self._requests

        # Check with Redis if available
        if redis_manager.is_enabled:
            allowed, remaining = redis_manager.check_rate_limit(
                client_id, limit, self._window
            )
        else:
            # Fallback: in-memory (not persistent)
            allowed, remaining = True, limit  # Simplified

        if not allowed:
            logger.warning(f"Rate limit exceeded for {client_id}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {self._window} seconds.",
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(self._window),
                },
            )

        return allowed, remaining


# Global rate limiter
rate_limiter = RateLimiter()


# ============================================================================
# Middleware Dependency
# ============================================================================

async def check_rate_limit_dependency(api_key: str = Security(get_api_key)):
    """
    Dependency for rate limiting.

    Args:
        api_key: Validated API key

    Raises:
        HTTPException: If rate limit exceeded
    """
    if not settings.rate_limit_enabled:
        return

    # Get custom limit for API key
    key_info = api_key_manager.validate_key(api_key)
    custom_limit = key_info.get("rate_limit") if key_info else None

    # Check rate limit
    await rate_limiter.check_rate_limit(api_key, custom_limit)
