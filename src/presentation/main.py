"""
Main FastAPI Application - Presentation Layer
Entry point for the Movie Streaming API with DDD + Clean Architecture + Performance Optimizations
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.gzip import GZipMiddleware

# Add src to path for imports
current_dir = Path(__file__).parent.parent.parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

from presentation.routers import movie_router, genre_router, auth_router
from presentation.middleware.rate_limiter import setup_rate_limiting
from presentation.middleware.compression import setup_compression
from presentation.middleware.performance import setup_performance_monitoring
from infrastructure.cache.cache_manager import get_cache_manager, close_cache_manager

# Create FastAPI application instance with performance optimizations
app = FastAPI(
    title="Movie Streaming API - Optimized",
    description="""
    A high-performance RESTful API for movie streaming platform built with FastAPI, DDD, and Clean Architecture.
    
    ## Performance Optimizations
    
    * **Caching**: Redis + Memory cache with intelligent fallback
    * **Rate Limiting**: Configurable rate limits per endpoint
    * **Compression**: Gzip compression for responses
    * **Async I/O**: Optimized async operations
    * **Search Indexing**: Fast search with pre-built indexes
    * **Connection Pooling**: Efficient resource management
    
    ## Features
    
    * **Authentication**: User registration, login, and JWT token-based auth
    * **Movies**: Browse, search, and filter movies with detailed ratings
    * **Genres**: Get available movie genres  
    * **Tags**: Search by movie tags
    * **Pagination**: All list endpoints support pagination
    * **Advanced Search**: Multiple search criteria including IMDB/TMDB integration
    * **Clean Architecture**: DDD principles with separated layers
    
    ## Architecture
    
    This API follows **Domain-Driven Design (DDD)** and **Clean Architecture** principles:
    
    - **Domain Layer**: Core business logic and entities
    - **Application Layer**: Use cases and business workflows
    - **Infrastructure Layer**: Data access (CSV file repository) with caching
    - **Presentation Layer**: FastAPI controllers and routes with middleware
    
    ## Authentication
    
    The API uses JWT tokens for authentication. Get your token via `/api/auth/login` 
    and include it in the Authorization header: `Bearer <your_token>`
    
    ## Data Source
    
    The API uses CSV files as data source with intelligent caching:
    - Movies data with ratings breakdown, IMDB/TMDB IDs, tags
    - User data for authentication
    
    ## Demo Accounts
    
    - Admin: `admin@movieapi.com` / `admin123`  
    - Demo: `demo@movieapi.com` / `demo123`
    
    ## Performance Monitoring
    
    - `/api/performance/stats` - Get performance and cache statistics
    - Response headers include timing information
    - Automatic logging of slow requests
    """,
    version="3.0.0",
    contact={
        "name": "Movie API Team",
        "email": "contact@movieapi.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# Setup performance optimizations
setup_performance_monitoring(app)
setup_rate_limiting(app)
setup_compression(app)

# Add Gzip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(movie_router)
app.include_router(genre_router)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint with cache status"""
    try:
        cache_manager = await get_cache_manager()
        cache_stats = cache_manager.get_stats()
        
        return {
            "status": "healthy",
            "message": "Movie Streaming API is running with optimizations",
            "version": "3.0.0",
            "cache_status": cache_stats,
            "features": [
                "Authentication (JWT)",
                "Movies with ratings breakdown", 
                "Genres and tags",
                "Advanced search",
                "IMDB/TMDB integration",
                "Clean Architecture",
                "Performance Optimizations",
                "Caching (Redis + Memory)",
                "Rate Limiting",
                "Response Compression"
            ]
        }
    except Exception as e:
        return {
            "status": "degraded",
            "message": "API is running but some optimizations may be unavailable",
            "version": "3.0.0",
            "error": str(e)
        }

# API Info endpoint
@app.get("/info", tags=["info"])
async def api_info():
    """API information and demo accounts"""
    return {
        "name": "Movie Streaming API - Optimized",
        "version": "3.0.0",
        "description": "High-performance movie streaming API with authentication and advanced features",
        "performance_features": [
            "Redis + Memory caching",
            "Rate limiting",
            "Response compression",
            "Async I/O optimization",
            "Search indexing",
            "Performance monitoring"
        ],
        "demo_accounts": {
            "admin": {
                "email": "admin@movieapi.com",
                "username": "admin", 
                "password": "admin123",
                "role": "superuser"
            },
            "demo": {
                "email": "demo@movieapi.com",
                "username": "demo",
                "password": "demo123", 
                "role": "user"
            }
        },
        "endpoints": {
            "authentication": "/api/auth/*",
            "movies": "/api/movies/*",
            "genres": "/api/genres/*",
            "performance": "/api/performance/*"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        }
    }

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Movie Streaming API - Optimized",
        version="3.0.0",
        description="A high-performance movie streaming API built with FastAPI, DDD, Clean Architecture, JWT Authentication, and performance optimizations",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "status_code": 500,
            "path": str(request.url)
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event with cache initialization"""
    print("🚀 Movie Streaming API v3.0.0 (Optimized with Parquet) is starting up...")
    print("🔐 Authentication: JWT-based with login/register")
    print("🎭 Movies: Advanced ratings and IMDB/TMDB integration")
    print("⚡ Performance: Caching, rate limiting, compression")
    print("📊 Monitoring: Performance tracking and statistics")
    print("📁 Data Format: Parquet (optimized for fast reading)")
    print("📚 API Documentation available at: /docs")
    print("🔄 Alternative documentation at: /redoc")
    print("💡 Demo accounts: /info")
    print("📈 Performance stats: /api/performance/stats")
    
    # Initialize cache
    try:
        cache_manager = await get_cache_manager()
        cache_type = cache_manager.get_cache_type()
        print(f"💾 Cache initialized: {cache_type}")
    except Exception as e:
        print(f"⚠️  Cache initialization failed: {e}")
    
    # Check Parquet files
    try:
        import os
        from pathlib import Path
        
        data_dir = Path("data")
        movies_parquet = data_dir / "movies.parquet"
        users_parquet = data_dir / "users.parquet"
        
        if movies_parquet.exists():
            print(f"📁 Movies data: Parquet format ({movies_parquet})")
        else:
            print(f"⚠️  Movies Parquet file not found: {movies_parquet}")
            print("💡 Run: python convert_csv_to_parquet.py to convert CSV to Parquet")
        
        if users_parquet.exists():
            print(f"📁 Users data: Parquet format ({users_parquet})")
        else:
            print(f"⚠️  Users Parquet file not found: {users_parquet}")
            
    except Exception as e:
        print(f"⚠️  Error checking Parquet files: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event with cache cleanup"""
    print("🎬 Movie Streaming API is shutting down...")
    
    # Close cache connections
    try:
        await close_cache_manager()
        print("💾 Cache connections closed")
    except Exception as e:
        print(f"⚠️  Error closing cache: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 