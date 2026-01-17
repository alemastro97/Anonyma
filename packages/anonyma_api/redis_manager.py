"""
Redis Manager for persistent job storage.

Handles:
- Job state persistence
- Distributed job tracking
- Cache management
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime
import redis
from .config import settings

from anonyma_core.logging_config import get_logger

logger = get_logger(__name__)


class RedisManager:
    """
    Redis manager for job persistence and caching.

    Features:
    - Persistent job storage
    - TTL-based expiration
    - Atomic operations
    - Connection pooling
    """

    def __init__(self):
        """Initialize Redis connection"""
        self._client: Optional[redis.Redis] = None
        self._enabled = settings.redis_enabled

        if self._enabled:
            try:
                self._client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                )
                # Test connection
                self._client.ping()
                logger.info("Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._enabled = False
                self._client = None

    @property
    def is_enabled(self) -> bool:
        """Check if Redis is enabled and connected"""
        return self._enabled and self._client is not None

    def _job_key(self, job_id: str) -> str:
        """Generate Redis key for job"""
        return f"job:{job_id}"

    def _cache_key(self, key: str) -> str:
        """Generate Redis key for cache"""
        return f"cache:{key}"

    # ========================================================================
    # Job Management
    # ========================================================================

    def save_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """
        Save job data to Redis.

        Args:
            job_id: Job identifier
            job_data: Job data dictionary

        Returns:
            True if saved successfully
        """
        if not self.is_enabled:
            return False

        try:
            key = self._job_key(job_id)

            # Add timestamp
            job_data["updated_at"] = datetime.utcnow().isoformat()

            # Save with TTL
            self._client.setex(
                key,
                settings.redis_job_ttl,
                json.dumps(job_data)
            )

            logger.debug(f"Job {job_id} saved to Redis")
            return True

        except Exception as e:
            logger.error(f"Failed to save job to Redis: {e}")
            return False

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job data from Redis.

        Args:
            job_id: Job identifier

        Returns:
            Job data or None if not found
        """
        if not self.is_enabled:
            return None

        try:
            key = self._job_key(job_id)
            data = self._client.get(key)

            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"Failed to get job from Redis: {e}")
            return None

    def delete_job(self, job_id: str) -> bool:
        """
        Delete job from Redis.

        Args:
            job_id: Job identifier

        Returns:
            True if deleted successfully
        """
        if not self.is_enabled:
            return False

        try:
            key = self._job_key(job_id)
            self._client.delete(key)
            logger.debug(f"Job {job_id} deleted from Redis")
            return True

        except Exception as e:
            logger.error(f"Failed to delete job from Redis: {e}")
            return False

    def update_job_status(self, job_id: str, status: str, progress: float = None, **kwargs) -> bool:
        """
        Update job status atomically.

        Args:
            job_id: Job identifier
            status: New status
            progress: Optional progress value
            **kwargs: Additional fields to update (e.g., error, result, output_file)

        Returns:
            True if updated successfully
        """
        if not self.is_enabled:
            return False

        try:
            job_data = self.get_job(job_id)
            if not job_data:
                return False

            job_data["status"] = status
            if progress is not None:
                job_data["progress"] = progress

            # Update additional fields
            for key, value in kwargs.items():
                job_data[key] = value

            return self.save_job(job_id, job_data)

        except Exception as e:
            logger.error(f"Failed to update job status: {e}")
            return False

    def list_jobs(self, pattern: str = "*") -> list:
        """
        List all job IDs matching pattern.

        Args:
            pattern: Pattern to match (e.g., "job:*")

        Returns:
            List of job IDs
        """
        if not self.is_enabled:
            return []

        try:
            keys = self._client.keys(f"job:{pattern}")
            return [key.replace("job:", "") for key in keys]

        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")
            return []

    # ========================================================================
    # Cache Management
    # ========================================================================

    def cache_set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set cache value.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default from settings)

        Returns:
            True if cached successfully
        """
        if not self.is_enabled:
            return False

        try:
            cache_key = self._cache_key(key)
            ttl = ttl or settings.cache_ttl

            self._client.setex(
                cache_key,
                ttl,
                json.dumps(value)
            )

            logger.debug(f"Cached key: {key}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache value: {e}")
            return False

    def cache_get(self, key: str) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.is_enabled:
            return None

        try:
            cache_key = self._cache_key(key)
            data = self._client.get(cache_key)

            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"Failed to get cached value: {e}")
            return None

    def cache_delete(self, key: str) -> bool:
        """
        Delete cached value.

        Args:
            key: Cache key

        Returns:
            True if deleted successfully
        """
        if not self.is_enabled:
            return False

        try:
            cache_key = self._cache_key(key)
            self._client.delete(cache_key)
            return True

        except Exception as e:
            logger.error(f"Failed to delete cached value: {e}")
            return False

    # ========================================================================
    # Rate Limiting
    # ========================================================================

    def check_rate_limit(self, client_id: str, limit: int, window: int) -> tuple[bool, int]:
        """
        Check rate limit for client.

        Args:
            client_id: Client identifier (API key or IP)
            limit: Max requests in window
            window: Window size in seconds

        Returns:
            (allowed, remaining) tuple
        """
        if not self.is_enabled:
            return True, limit

        try:
            key = f"ratelimit:{client_id}"

            # Increment counter
            count = self._client.incr(key)

            # Set expiration on first request
            if count == 1:
                self._client.expire(key, window)

            allowed = count <= limit
            remaining = max(0, limit - count)

            return allowed, remaining

        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            return True, limit  # Allow on error

    # ========================================================================
    # Utilities
    # ========================================================================

    def ping(self) -> bool:
        """
        Test Redis connection.

        Returns:
            True if connection is healthy
        """
        if not self.is_enabled:
            return False

        try:
            return self._client.ping()
        except Exception:
            return False

    def flushdb(self) -> bool:
        """
        Clear all data (USE WITH CAUTION).

        Returns:
            True if cleared successfully
        """
        if not self.is_enabled:
            return False

        try:
            self._client.flushdb()
            logger.warning("Redis database flushed")
            return True
        except Exception as e:
            logger.error(f"Failed to flush database: {e}")
            return False

    def close(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            logger.info("Redis connection closed")


# Global Redis manager instance
redis_manager = RedisManager()
