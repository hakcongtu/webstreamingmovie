"""
Movie Use Cases - Application Layer
Orchestrates business logic for movie operations
"""
from typing import List, Optional

from domain.entities.movie import Movie
from domain.entities.genre import Genre
from domain.repositories.movie_repository import IMovieRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from domain.value_objects.search_criteria import SearchCriteria

from application.dtos.movie_schemas import (
    PaginatedResponseDto,
    MovieDetailResponseDto,
    GenreListResponseDto,
    SearchRequestDto,
    MovieDto,
    MovieCreateDto
)
from application.mappers.movie_mapper import MovieMapper, GenreMapper


class MovieUseCase:
    """
    Movie Use Case - Application Layer
    Orchestrates movie-related business operations
    """

    def __init__(self, movie_repository: IMovieRepository):
        self._movie_repository = movie_repository

    async def get_movies(self, page: int = 1, limit: int = 10) -> PaginatedResponseDto:
        """
        Get all movies with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_all(pagination)
        return MovieMapper.to_paginated_response(result)
    
    async def create_movie(self, movie_dto: MovieCreateDto) -> MovieDto:
        """
        Create a new movie
        """
        # Convert DTO to domain entity
        movie_entity = MovieMapper.from_create_dto(movie_dto)
        # Create movie in repository
        created_movie = await self._movie_repository.create(movie_entity)
        # Convert back to DTO for response
        return MovieMapper.to_dto(created_movie)

    async def get_movie_by_id(self, movie_id: str) -> Optional[MovieDetailResponseDto]:
        """
        Get movie by ID with related movies
        """
        movie = await self._movie_repository.find_by_id(movie_id)
        if not movie:
            return None

        # Get related movies (same genres)
        related_movies = await self._movie_repository.find_related_movies(movie, limit=5)
        
        return MovieMapper.to_detail_response(movie, related_movies)

    async def search_movies(self, search_request: SearchRequestDto) -> PaginatedResponseDto:
        """
        Search movies with criteria and pagination
        """
        # Create search criteria from request
        criteria = SearchCriteria(
            title=search_request.title,
            genre=search_request.genre,
            year=search_request.year,
            min_rating=search_request.min_rating,
            max_rating=search_request.max_rating
        )

        pagination = PaginationParams(
            page=search_request.page,
            limit=search_request.limit
        )

        result = await self._movie_repository.search(criteria, pagination)
        return MovieMapper.to_paginated_response(result)

    async def get_movies_by_genre(
        self, 
        genre: str, 
        page: int = 1, 
        limit: int = 10
    ) -> PaginatedResponseDto:
        """
        Get movies by genre with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_by_genre(genre, pagination)
        return MovieMapper.to_paginated_response(result)

    async def get_popular_movies(self, page: int = 1, limit: int = 10) -> PaginatedResponseDto:
        """
        Get popular movies (by ratings count) with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_popular(pagination)
        return MovieMapper.to_paginated_response(result)

    async def get_highly_rated_movies(
        self, 
        page: int = 1, 
        limit: int = 10
    ) -> PaginatedResponseDto:
        """
        Get highly rated movies with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_highly_rated(pagination)
        return MovieMapper.to_paginated_response(result)

    async def get_recent_movies(self, page: int = 1, limit: int = 10) -> PaginatedResponseDto:
        """
        Get recent movies with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_recent(pagination)
        return MovieMapper.to_paginated_response(result)

    async def increment_movie_views(self, movie_id: str) -> Optional[Movie]:
        """
        Increment movie view count
        """
        return await self._movie_repository.update_views(movie_id)

    async def get_all_genres(self) -> GenreListResponseDto:
        """
        Get all available genres
        """
        genres = await self._movie_repository.find_all_genres()
        genre_dtos = GenreMapper.to_dto_list(genres)
        
        return GenreListResponseDto(
            genres=genre_dtos,
            total=len(genre_dtos)
        )

    async def get_movie_statistics(self) -> dict:
        """
        Get movie statistics
        """
        total_movies = await self._movie_repository.get_total_count()
        genres = await self._movie_repository.find_all_genres()
        
        # Get some popular movies for stats
        popular_result = await self._movie_repository.find_popular(
            PaginationParams(page=1, limit=5)
        )
        
        # Get highly rated movies for stats
        rated_result = await self._movie_repository.find_highly_rated(
            PaginationParams(page=1, limit=5)
        )

        return {
            "total_movies": total_movies,
            "total_genres": len(genres),
            "most_popular": MovieMapper.to_summary_dto_list(popular_result.data),
            "highest_rated": MovieMapper.to_summary_dto_list(rated_result.data)
        }

    async def get_movies_by_tag(
        self, 
        tag: str, 
        page: int = 1, 
        limit: int = 10
    ) -> PaginatedResponseDto:
        """
        Get movies by tag with pagination
        """
        pagination = PaginationParams(page=page, limit=limit)
        result = await self._movie_repository.find_by_tag(tag, pagination)
        return MovieMapper.to_paginated_response(result)

    async def get_movie_by_imdb_id(self, imdb_id: str) -> Optional[MovieDetailResponseDto]:
        """
        Get movie by IMDB ID with related movies
        """
        movie = await self._movie_repository.find_by_imdb_id(imdb_id)
        if not movie:
            return None

        # Get related movies (same genres)
        related_movies = await self._movie_repository.find_related_movies(movie, limit=5)
        
        return MovieMapper.to_detail_response(movie, related_movies)

    async def get_movie_by_tmdb_id(self, tmdb_id: str) -> Optional[MovieDetailResponseDto]:
        """
        Get movie by TMDB ID with related movies
        """
        movie = await self._movie_repository.find_by_tmdb_id(tmdb_id)
        if not movie:
            return None

        # Get related movies (same genres)
        related_movies = await self._movie_repository.find_related_movies(movie, limit=5)
        
        return MovieMapper.to_detail_response(movie, related_movies) 