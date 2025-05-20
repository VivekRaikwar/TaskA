from typing import Any, Optional
import json
import hashlib
import redis
import logging
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_CONNECTION_URL,
            decode_responses=True
        )
        self.default_ttl = settings.CACHE_TTL
        self.prefix = settings.CACHE_PREFIX

    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from prefix and data."""
        if isinstance(data, (dict, list)):
            data = json.dumps(data, sort_keys=True)
        elif not isinstance(data, str):
            data = str(data)
        
        hash_obj = hashlib.md5(data.encode())
        return f"{self.prefix}:{prefix}:{hash_obj.hexdigest()}"

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("cache_get_error", key=key, error=str(e))
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache."""
        try:
            serialized = json.dumps(value)
            return self.redis_client.setex(
                key,
                ttl or self.default_ttl,
                serialized
            )
        except Exception as e:
            logger.error("cache_set_error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            logger.error("cache_delete_error", key=key, error=str(e))
            return False

    def get_or_set(
        self,
        key: str,
        value_func: callable,
        ttl: Optional[int] = None
    ) -> Any:
        """Get value from cache or set it if not exists."""
        value = self.get(key)
        if value is not None:
            return value

        value = value_func()
        self.set(key, value, ttl)
        return value

    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        try:
            keys = self.redis_client.keys(f"{self.prefix}:{pattern}:*")
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("cache_invalidate_error", pattern=pattern, error=str(e))
            return 0

# Create singleton instance
cache_service = CacheService() 