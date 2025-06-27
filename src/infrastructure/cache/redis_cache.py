"""
Redis Cache Implementation - Infrastructure Layer
Provides high-performance caching using Redis
"""
import json
import pickle
from typing import Any, Optional, Union
import aioredis
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis Cache Implementation
    Provides high-performance caching with Redis
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._default_ttl = 3600  # 1 hour default
    
    async def connect(self):
        """Connect to Redis"""
        if self._redis is None:
            try:
                self._redis = aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                await self._redis.ping()
                logger.info("Connected to Redis cache")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._redis = None
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self._redis:
            return None
        
        try:
            value = await self._redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        if not self._redis:
            return False
        
        try:
            ttl = ttl or self._default_ttl
            await self._redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self._redis:
            return False
        
        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self._redis:
            return False
        
        try:
            return await self._redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self._redis:
            return 0
        
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                return await self._redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Error clearing cache pattern: {e}")
            return 0


# Global cache instance
_cache_instance: Optional[RedisCache] = None


async def get_cache() -> RedisCache:
    """Get global cache instance"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = RedisCache()
        await _cache_instance.connect()
    return _cache_instance


async def close_cache():
    """Close global cache instance"""
    global _cache_instance
    if _cache_instance:
        await _cache_instance.disconnect()
        _cache_instance = None 