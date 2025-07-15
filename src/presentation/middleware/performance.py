"""
Performance Monitoring Middleware - Presentation Layer
Provides performance monitoring and logging
"""
import time
import logging
from typing import Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)

# Performance thresholds
SLOW_REQUEST_THRESHOLD = 1.0  # seconds
VERY_SLOW_REQUEST_THRESHOLD = 5.0  # seconds

class PerformanceMonitor:
    """Performance monitoring utility"""
    
    def __init__(self):
        self.request_count = 0
        self.slow_requests = 0
        self.error_count = 0
        self.total_response_time = 0.0
    
    def record_request(self, path: str, method: str, duration: float, status_code: int):
        """Record request performance metrics"""
        self.request_count += 1
        self.total_response_time += duration
        
        # Log slow requests
        if duration > VERY_SLOW_REQUEST_THRESHOLD:
            logger.error(f"VERY SLOW REQUEST: {method} {path} took {duration:.3f}s (Status: {status_code})")
            self.slow_requests += 1
        elif duration > SLOW_REQUEST_THRESHOLD:
            logger.warning(f"SLOW REQUEST: {method} {path} took {duration:.3f}s (Status: {status_code})")
            self.slow_requests += 1
        
        # Log errors
        if status_code >= 400:
            self.error_count += 1
            logger.error(f"ERROR REQUEST: {method} {path} returned {status_code} in {duration:.3f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "slow_requests": self.slow_requests,
            "error_count": self.error_count,
            "average_response_time": round(avg_response_time, 3),
            "total_response_time": round(self.total_response_time, 3)
        }

# Global performance monitor
performance_monitor = PerformanceMonitor()

async def performance_middleware(request: Request, call_next):
    """Performance monitoring middleware"""
    start_time = time.time()
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        performance_monitor.record_request(
            path=str(request.url.path),
            method=request.method,
            duration=duration,
            status_code=response.status_code
        )
        
        # Add performance headers
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        response.headers["X-Request-ID"] = str(hash(f"{request.url.path}{start_time}"))
        
        return response
        
    except Exception as e:
        # Calculate duration for failed requests
        duration = time.time() - start_time
        
        # Record error
        performance_monitor.record_request(
            path=str(request.url.path),
            method=request.method,
            duration=duration,
            status_code=500
        )
        
        # Re-raise exception
        raise

def setup_performance_monitoring(app):
    """Setup performance monitoring for FastAPI app"""
    @app.middleware("http")
    async def performance_middleware_wrapper(request: Request, call_next):
        return await performance_middleware(request, call_next)
    
    # Add performance stats endpoint
    @app.get("/api/performance/stats", tags=["performance"])
    async def get_performance_stats():
        """Get performance statistics"""
        return {
            "performance_stats": performance_monitor.get_stats(),
            "cache_stats": await get_cache_stats()
        }

async def get_cache_stats():
    """Get cache statistics"""
    try:
        from infrastructure.cache.cache_manager import get_cache_manager
        cache_manager = await get_cache_manager()
        return cache_manager.get_stats()
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": "Unable to get cache stats"} 