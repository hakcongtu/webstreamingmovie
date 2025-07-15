"""
Presentation Routers Package
Contains all FastAPI routers for the movie streaming API
"""

from presentation.routers.movie_router import router as movie_router
from presentation.routers.genre_router import router as genre_router
from presentation.routers.auth_router import router as auth_router

__all__ = ["movie_router", "genre_router", "auth_router"] 