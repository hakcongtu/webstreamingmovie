"""
In-Memory Cache Implementation - Infrastructure Layer
Fallback cache when Redis is not available
"""
import time
import json
from typing import Any, Optional, Dict, Tuple
import logging
from threading import Lock

logger = logging.getLogger(__name__)


class MemoryCache:
    """
    In-Memory Cache Implementation
    Fallback cache when Redis is not available
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        with self._lock:
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time > expiry
            ]
            for key in expired_keys:
                del self._cache[key]
            
            self._last_cleanup = current_time
    
    def _evict_if_needed(self):
        """Evict oldest entries if cache is full"""
        if len(self._cache) >= self._max_size:
            with self._lock:
                # Remove oldest entries (LRU-like)
                sorted_items = sorted(
                    self._cache.items(),
                    key=lambda x: x[1][1]  # Sort by expiry time
                )
                # Remove 10% of oldest entries
                to_remove = max(1, len(sorted_items) // 10)
                for key, _ in sorted_items[:to_remove]:
                    del self._cache[key]
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        self._cleanup_expired()
        
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    del self._cache[key]
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self._default_ttl
            expiry = time.time() + ttl
            
            with self._lock:
                self._cache[key] = (value, expiry)
                self._evict_if_needed()
            
            return True
        except Exception as e:
            logger.error(f"Error setting memory cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            with self._lock:
                if key in self._cache:
                    del self._cache[key]
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deleting from memory cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        self._cleanup_expired()
        
        with self._lock:
            if key in self._cache:
                _, expiry = self._cache[key]
                return time.time() < expiry
        
        return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern (simple string matching)"""
        try:
            count = 0
            with self._lock:
                keys_to_remove = [
                    key for key in self._cache.keys()
                    if pattern in key
                ]
                for key in keys_to_remove:
                    del self._cache[key]
                    count += 1
            return count
        except Exception as e:
            logger.error(f"Error clearing memory cache pattern: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "usage_percent": (len(self._cache) / self._max_size) * 100
            }


# Global memory cache instance
_memory_cache_instance: Optional[MemoryCache] = None


async def get_memory_cache() -> MemoryCache:
    """Get global memory cache instance"""
    global _memory_cache_instance
    if _memory_cache_instance is None:
        _memory_cache_instance = MemoryCache()
    return _memory_cache_instance 