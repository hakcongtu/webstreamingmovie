"""
Movie Repository Interface - Domain Layer
Defines the contract for movie data access without implementation details
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.movie import Movie
from ..entities.genre import Genre
from ..value_objects.pagination import PaginationParams, PaginatedResult
from ..value_objects.search_criteria import SearchCriteria


class IMovieRepository(ABC):
    """
    Movie Repository Interface - Domain Layer
    Defines the contract for movie data access without implementation details
    """

    @abstractmethod
    async def find_all(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get all movies with pagination"""
        pass

    @abstractmethod
    async def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """Find movie by ID"""
        pass

    @abstractmethod
    async def search(
        self, 
        criteria: SearchCriteria, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Search movies with criteria and pagination"""
        pass

    @abstractmethod
    async def find_by_genre(
        self, 
        genre: str, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Get movies by genre with pagination"""
        pass

    @abstractmethod
    async def find_all_genres(self) -> List[Genre]:
        """Get all available genres"""
        pass

    @abstractmethod
    async def find_popular(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get popular movies (by views) with pagination"""
        pass

    @abstractmethod
    async def find_highly_rated(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get highly rated movies with pagination"""
        pass

    @abstractmethod
    async def find_recent(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get recent movies with pagination"""
        pass

    @abstractmethod
    async def update_views(self, movie_id: str) -> Optional[Movie]:
        """Update movie view count"""
        pass

    @abstractmethod
    async def get_total_count(self) -> int:
        """Get total count of movies"""
        pass

    @abstractmethod
    async def find_related_movies(self, movie: Movie, limit: int = 5) -> List[Movie]:
        """Find movies related to the given movie (same genres)"""
        pass 

    @abstractmethod
    async def create(self, movie: Movie) -> Movie:
        """Create a new movie"""
        pass