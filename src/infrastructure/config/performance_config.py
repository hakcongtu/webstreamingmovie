"""
Performance Configuration - Infrastructure Layer
Configuration settings for performance optimizations
"""
import os
from typing import Dict, Any

class PerformanceConfig:
    """Performance configuration settings"""
    
    # Cache settings
    CACHE_TTL = {
        "movies_data": 1800,  # 30 minutes
        "movie_detail": 1800,  # 30 minutes
        "genres_list": 3600,   # 1 hour
        "search_results": 900,  # 15 minutes
        "statistics": 1800,     # 30 minutes
        "total_count": 3600     # 1 hour
    }
    
    # Rate limiting settings
    RATE_LIMITS = {
        "default": "100/minute",
        "auth": "10/minute",
        "search": "50/minute",
        "movies": "200/minute",
        "genres": "100/minute",
        "performance": "20/minute"
    }
    
    # Performance thresholds
    PERFORMANCE_THRESHOLDS = {
        "slow_request": 1.0,      # seconds
        "very_slow_request": 5.0,  # seconds
        "min_compression_size": 1024,  # bytes
    }
    
    # Search optimization settings
    SEARCH_OPTIMIZATION = {
        "chunk_size": 1000,       # Process CSV in chunks
        "index_cache_ttl": 3600,  # Search index cache TTL
        "max_search_results": 1000  # Maximum search results
    }
    
    # Compression settings
    COMPRESSION = {
        "enabled": True,
        "min_size": 1024,
        "level": 6,
        "content_types": [
            "application/json",
            "text/plain",
            "text/html",
            "text/css",
            "application/javascript"
        ]
    }
    
    # Memory cache settings
    MEMORY_CACHE = {
        "max_size": 1000,
        "default_ttl": 3600,
        "cleanup_interval": 300
    }
    
    # Redis settings
    REDIS = {
        "url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "max_connections": 10,
        "socket_timeout": 5,
        "socket_connect_timeout": 2
    }
    
    @classmethod
    def get_cache_ttl(cls, cache_type: str) -> int:
        """Get TTL for cache type"""
        return cls.CACHE_TTL.get(cache_type, 1800)
    
    @classmethod
    def get_rate_limit(cls, endpoint_type: str) -> str:
        """Get rate limit for endpoint type"""
        return cls.RATE_LIMITS.get(endpoint_type, cls.RATE_LIMITS["default"])
    
    @classmethod
    def get_performance_config(cls) -> Dict[str, Any]:
        """Get all performance configuration"""
        return {
            "cache_ttl": cls.CACHE_TTL,
            "rate_limits": cls.RATE_LIMITS,
            "performance_thresholds": cls.PERFORMANCE_THRESHOLDS,
            "search_optimization": cls.SEARCH_OPTIMIZATION,
            "compression": cls.COMPRESSION,
            "memory_cache": cls.MEMORY_CACHE,
            "redis": cls.REDIS
        } 