"""
Compression Middleware - Presentation Layer
Provides response compression for better performance
"""
import gzip
import json
from typing import Union
from fastapi import Request, Response
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

# Minimum size for compression (bytes)
MIN_COMPRESSION_SIZE = 1024

# Content types that should be compressed
COMPRESSIBLE_CONTENT_TYPES = {
    "application/json",
    "text/plain",
    "text/html",
    "text/css",
    "application/javascript",
    "text/javascript"
}

def should_compress(content_type: str, content_length: int) -> bool:
    """Check if response should be compressed"""
    return (
        content_length >= MIN_COMPRESSION_SIZE and
        any(ct in content_type for ct in COMPRESSIBLE_CONTENT_TYPES)
    )

def compress_content(content: Union[str, bytes]) -> bytes:
    """Compress content using gzip"""
    if isinstance(content, str):
        content = content.encode('utf-8')
    
    return gzip.compress(content, compresslevel=6)

async def compression_middleware(request: Request, call_next):
    """Compression middleware"""
    # Check if client accepts gzip
    accept_encoding = request.headers.get("accept-encoding", "")
    supports_gzip = "gzip" in accept_encoding.lower()
    
    if not supports_gzip:
        return await call_next(request)
    
    # Process request
    response = await call_next(request)
    
    # Check if response should be compressed
    content_type = response.headers.get("content-type", "")
    content_length = response.headers.get("content-length")
    
    if content_length:
        content_length = int(content_length)
    else:
        content_length = 0
    
    if not should_compress(content_type, content_length):
        return response
    
    # Get response content
    if hasattr(response, 'body'):
        content = response.body
    else:
        # For streaming responses, we can't easily compress
        return response
    
    # Compress content
    compressed_content = compress_content(content)
    
    # Create new response with compression
    compressed_response = Response(
        content=compressed_content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
    
    # Add compression headers
    compressed_response.headers["content-encoding"] = "gzip"
    compressed_response.headers["content-length"] = str(len(compressed_content))
    
    # Remove original content-length if it exists
    if "content-length" in compressed_response.headers:
        del compressed_response.headers["content-length"]
    
    return compressed_response

def setup_compression(app):
    """Setup compression middleware for FastAPI app"""
    @app.middleware("http")
    async def compression_middleware_wrapper(request: Request, call_next):
        return await compression_middleware(request, call_next) 