"""
Main FastAPI Application - Presentation Layer
Entry point for the Movie Streaming API with DDD + Clean Architecture
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

# Create FastAPI application instance
app = FastAPI(
    title="Movie Streaming API",
    description="""
    A RESTful API for movie streaming platform built with FastAPI, DDD, and Clean Architecture.
    
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
    - **Infrastructure Layer**: Data access (CSV file repository)
    - **Presentation Layer**: FastAPI controllers and routes
    
    ## Authentication
    
    The API uses JWT tokens for authentication. Get your token via `/api/auth/login` 
    and include it in the Authorization header: `Bearer <your_token>`
    
    ## Data Source
    
    The API uses CSV files as data source:
    - Movies data with ratings breakdown, IMDB/TMDB IDs, tags
    - User data for authentication
    
    ## Demo Accounts
    
    - Admin: `admin@movieapi.com` / `admin123`  
    - Demo: `demo@movieapi.com` / `demo123`
    """,
    version="2.0.0",
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
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "Movie Streaming API is running",
        "version": "2.0.0",
        "features": [
            "Authentication (JWT)",
            "Movies with ratings breakdown", 
            "Genres and tags",
            "Advanced search",
            "IMDB/TMDB integration",
            "Clean Architecture"
        ]
    }

# API Info endpoint
@app.get("/info", tags=["info"])
async def api_info():
    """API information and demo accounts"""
    return {
        "name": "Movie Streaming API",
        "version": "2.0.0",
        "description": "Movie streaming API with authentication and advanced features",
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
            "genres": "/api/genres/*"
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
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle global exceptions"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print("🚀 Movie Streaming API starting up...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔄 Alternative docs: http://localhost:8000/redoc")
    print("💓 Health check: http://localhost:8000/health")
    print("=" * 60)
    # Seed data
    from src.infrastructure.database.seed_data import seed_users
    await seed_users()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("🛑 Movie Streaming API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 