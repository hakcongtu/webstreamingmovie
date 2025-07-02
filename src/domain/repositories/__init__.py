"""
Domain Repositories Package
Contains repository interfaces for the movie streaming API
"""

from .movie_repository import IMovieRepository
from .user_repository import IUserRepository

__all__ = ["IMovieRepository", "IUserRepository"] 