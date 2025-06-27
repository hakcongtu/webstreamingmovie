"""
Cache Manager - Infrastructure Layer
Manages both Redis and memory cache with fallback strategy
"""
import logging
from typing import Any, Optional
from .redis_cache import RedisCache
from .memory_cache import MemoryCache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Cache Manager
    Provides unified caching interface with Redis fallback to memory
    """
    
    def __init__(self):
        self._redis_cache: Optional[RedisCache] = None
        self._memory_cache: Optional[MemoryCache] = None
        self._use_redis = True
    
    async def initialize(self):
        """Initialize cache manager"""
        try:
            # Try Redis first
            self._redis_cache = RedisCache()
            await self._redis_cache.connect()
            self._use_redis = True
            logger.info("Using Redis cache")
        except Exception as e:
            logger.warning(f"Redis not available, falling back to memory cache: {e}")
            self._use_redis = False
            self._memory_cache = MemoryCache()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self._use_redis and self._redis_cache:
            try:
                return await self._redis_cache.get(key)
            except Exception as e:
                logger.error(f"Redis get error, falling back to memory: {e}")
                self._use_redis = False
                if not self._memory_cache:
                    self._memory_cache = MemoryCache()
        
        if self._memory_cache:
            return await self._memory_cache.get(key)
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        success = False
        
        if self._use_redis and self._redis_cache:
            try:
                success = await self._redis_cache.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Redis set error, falling back to memory: {e}")
                self._use_redis = False
                if not self._memory_cache:
                    self._memory_cache = MemoryCache()
        
        if not success and self._memory_cache:
            success = await self._memory_cache.set(key, value, ttl)
        
        return success
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        success = False
        
        if self._use_redis and self._redis_cache:
            try:
                success = await self._redis_cache.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if self._memory_cache:
            memory_success = await self._memory_cache.delete(key)
            success = success or memory_success
        
        return success
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if self._use_redis and self._redis_cache:
            try:
                return await self._redis_cache.exists(key)
            except Exception as e:
                logger.error(f"Redis exists error: {e}")
        
        if self._memory_cache:
            return await self._memory_cache.exists(key)
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        count = 0
        
        if self._use_redis and self._redis_cache:
            try:
                count += await self._redis_cache.clear_pattern(pattern)
            except Exception as e:
                logger.error(f"Redis clear pattern error: {e}")
        
        if self._memory_cache:
            count += await self._memory_cache.clear_pattern(pattern)
        
        return count
    
    async def close(self):
        """Close cache connections"""
        if self._redis_cache:
            await self._redis_cache.disconnect()
        
        self._redis_cache = None
        self._memory_cache = None
    
    def get_cache_type(self) -> str:
        """Get current cache type"""
        if self._use_redis and self._redis_cache:
            return "redis"
        elif self._memory_cache:
            return "memory"
        else:
            return "none"
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        stats = {
            "type": self.get_cache_type(),
            "redis_available": self._use_redis and self._redis_cache is not None
        }
        
        if self._memory_cache:
            stats["memory"] = self._memory_cache.get_stats()
        
        return stats


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager


async def close_cache_manager():
    """Close global cache manager"""
    global _cache_manager
    if _cache_manager:
        await _cache_manager.close()
        _cache_manager = None 