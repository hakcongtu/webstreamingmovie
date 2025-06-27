"""
Rate Limiting Middleware - Presentation Layer
Provides rate limiting functionality using slowapi
"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Rate limit configurations
RATE_LIMITS = {
    "default": "100/minute",
    "auth": "10/minute",
    "search": "50/minute",
    "movies": "200/minute",
    "genres": "100/minute"
}

def get_rate_limit_for_path(path: str) -> str:
    """Get appropriate rate limit for path"""
    if path.startswith("/api/auth"):
        return RATE_LIMITS["auth"]
    elif path.startswith("/api/movies/search"):
        return RATE_LIMITS["search"]
    elif path.startswith("/api/movies"):
        return RATE_LIMITS["movies"]
    elif path.startswith("/api/genres"):
        return RATE_LIMITS["genres"]
    else:
        return RATE_LIMITS["default"]

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    try:
        # Get rate limit for this path
        rate_limit = get_rate_limit_for_path(request.url.path)
        
        # Apply rate limiting
        limiter.limit(rate_limit)(lambda: None)()
        
        # Process request
        response = await call_next(request)
        return response
        
    except RateLimitExceeded as e:
        logger.warning(f"Rate limit exceeded for {request.client.host}: {request.url.path}")
        return _rate_limit_exceeded_handler(request, e)

def setup_rate_limiting(app):
    """Setup rate limiting for FastAPI app"""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Add rate limiting to all routes
    @app.middleware("http")
    async def rate_limit_middleware_wrapper(request: Request, call_next):
        return await rate_limit_middleware(request, call_next) 