"""
Movie Mapper - Application Layer
Converts between domain entities and DTOs
"""
from typing import List

from domain.entities.movie import Movie
from domain.entities.genre import Genre
from domain.value_objects.pagination import PaginatedResult

from application.dtos.movie_schemas import (
    MovieDto,
    MovieSummaryDto,
    GenreDto,
    PaginatedResponseDto,
    PaginationMetaDto,
    MovieDetailResponseDto,
    MovieStatsDto,
    TagDto
)


class MovieMapper:
    """
    Movie Mapper - Application Layer
    Converts between domain entities and DTOs
    """

    @staticmethod
    def to_dto(movie: Movie) -> MovieDto:
        """Convert Movie entity to MovieDto"""
        return MovieDto(
            movieId=movie.movieId,
            title=movie.title,
            genres=movie.genres,
            imdb_id=movie.imdb_id,
            tmdb_id=movie.tmdb_id,
            ratings_count=movie.ratings_count,
            zero_to_one_ratings_count=movie.zero_to_one_ratings_count,
            one_to_two_ratings_count=movie.one_to_two_ratings_count,
            two_to_three_ratings_count=movie.two_to_three_ratings_count,
            three_to_four_ratings_count=movie.three_to_four_ratings_count,
            four_to_five_ratings_count=movie.four_to_five_ratings_count,
            average_rating=movie.average_rating,
            tags=movie.tags,
            earliest_rating=movie.earliest_rating,
            latest_rating=movie.latest_rating,
            earliest_tag=movie.earliest_tag,
            latest_tag=movie.latest_tag,
            
            # Computed fields
            is_highly_rated=movie.is_highly_rated(),
            is_popular=movie.is_popular(),
            primary_genre=movie.get_primary_genre(),
            rating_distribution=movie.get_rating_distribution(),
            positive_rating_percentage=movie.get_positive_rating_percentage(),
            negative_rating_percentage=movie.get_negative_rating_percentage()
        )

    @staticmethod
    def to_summary_dto(movie: Movie) -> MovieSummaryDto:
        """Convert Movie entity to MovieSummaryDto"""
        return MovieSummaryDto(
            movieId=movie.movieId,
            title=movie.title,
            genres=movie.genres,
            average_rating=movie.average_rating,
            ratings_count=movie.ratings_count,
            tags=movie.tags,
            latest_rating=movie.latest_rating,
            is_highly_rated=movie.is_highly_rated(),
            is_popular=movie.is_popular(),
            primary_genre=movie.get_primary_genre(),
            positive_rating_percentage=movie.get_positive_rating_percentage()
        )

    @staticmethod
    def to_dto_list(movies: List[Movie]) -> List[MovieDto]:
        """Convert list of Movie entities to MovieDto list"""
        return [MovieMapper.to_dto(movie) for movie in movies]

    @staticmethod
    def to_summary_dto_list(movies: List[Movie]) -> List[MovieSummaryDto]:
        """Convert list of Movie entities to MovieSummaryDto list"""
        return [MovieMapper.to_summary_dto(movie) for movie in movies]

    @staticmethod
    def to_paginated_response(result: PaginatedResult[Movie]) -> PaginatedResponseDto:
        """Convert PaginatedResult<Movie> to PaginatedResponseDto"""
        pagination_meta = PaginationMetaDto(
            page=result.page,
            limit=result.limit,
            total=result.total,
            total_pages=result.total_pages,
            has_next=result.has_next,
            has_previous=result.has_previous
        )

        return PaginatedResponseDto(
            data=MovieMapper.to_summary_dto_list(result.data),
            pagination=pagination_meta
        )

    @staticmethod
    def to_detail_response(movie: Movie, related_movies: List[Movie]) -> MovieDetailResponseDto:
        """Convert Movie and related movies to MovieDetailResponseDto"""
        return MovieDetailResponseDto(
            movie=MovieMapper.to_dto(movie),
            related_movies=MovieMapper.to_summary_dto_list(related_movies)
        )

    @staticmethod
    def to_stats_dto(
        movies: List[Movie],
        genres: List[Genre],
        most_popular: List[Movie],
        highest_rated: List[Movie],
        recent_movies: List[Movie]
    ) -> MovieStatsDto:
        """Convert movie statistics to MovieStatsDto"""
        # Calculate stats
        total_movies = len(movies)
        total_genres = len(genres)
        
        # Get all unique tags
        all_tags = set()
        for movie in movies:
            all_tags.update(movie.tags)
        total_tags = len(all_tags)
        
        # Calculate average rating
        avg_rating = sum(movie.average_rating for movie in movies) / total_movies if total_movies > 0 else 0
        
        # Calculate total ratings across all movies
        total_ratings = sum(movie.ratings_count for movie in movies)
        
        # Count highly rated and popular movies
        highly_rated_count = sum(1 for movie in movies if movie.is_highly_rated())
        popular_count = sum(1 for movie in movies if movie.is_popular())

        return MovieStatsDto(
            total_movies=total_movies,
            total_genres=total_genres,
            total_tags=total_tags,
            average_rating=round(avg_rating, 2),
            total_ratings=total_ratings,
            highly_rated_movies=highly_rated_count,
            popular_movies=popular_count,
            most_popular=MovieMapper.to_summary_dto_list(most_popular),
            highest_rated=MovieMapper.to_summary_dto_list(highest_rated)
            # recent_movies=MovieMapper.to_summary_dto_list(recent_movies)
        )

    @staticmethod
    def extract_tags_with_counts(movies: List[Movie]) -> List[TagDto]:
        """Extract tags with their counts from movies"""
        tag_counts = {}
        
        for movie in movies:
            for tag in movie.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count (descending) then by name
        sorted_tags = sorted(tag_counts.items(), key=lambda x: (-x[1], x[0]))
        
        return [
            TagDto(name=tag, count=count)
            for tag, count in sorted_tags
        ]

    @staticmethod
    def from_create_dto(movie_dto) -> Movie:
        """Convert MovieCreateDto to Movie entity"""
        return Movie(
            movieId=movie_dto.movieId,
            title=movie_dto.title,
            genres=movie_dto.genres,
            imdb_id=movie_dto.imdb_id,
            tmdb_id=movie_dto.tmdb_id,
            ratings_count=movie_dto.ratings_count,
            zero_to_one_ratings_count=movie_dto.zero_to_one_ratings_count,
            one_to_two_ratings_count=movie_dto.one_to_two_ratings_count,
            two_to_three_ratings_count=movie_dto.two_to_three_ratings_count,
            three_to_four_ratings_count=movie_dto.three_to_four_ratings_count,
            four_to_five_ratings_count=movie_dto.four_to_five_ratings_count,
            average_rating=movie_dto.average_rating,
            tags=movie_dto.tags,
            earliest_rating=movie_dto.earliest_rating,
            latest_rating=movie_dto.latest_rating,
            earliest_tag=movie_dto.earliest_tag,
            latest_tag=movie_dto.latest_tag
        )

    @staticmethod
    def from_database_data(movie_data: dict) -> Movie:
        """Convert database movie data to Movie entity with default values for missing fields"""
        return Movie(
            movieId=str(movie_data.get('movieId', '')),
            title=movie_data.get('title', ''),
            genres=[g.strip() for g in movie_data.get('genres', '').split('|') if g and g.strip()] if movie_data.get('genres') else [],
            imdb_id=movie_data.get('imdb_id', ''),
            tmdb_id=movie_data.get('tmdb_id', ''),
            ratings_count=movie_data.get('ratings_count', 0),
            zero_to_one_ratings_count=movie_data.get('zero_to_one_ratings_count', 0),
            one_to_two_ratings_count=movie_data.get('one_to_two_ratings_count', 0),
            two_to_three_ratings_count=movie_data.get('two_to_three_ratings_count', 0),
            three_to_four_ratings_count=movie_data.get('three_to_four_ratings_count', 0),
            four_to_five_ratings_count=movie_data.get('four_to_five_ratings_count', 0),
            average_rating=movie_data.get('average_rating', 0.0),
            tags=movie_data.get('tags', '').split('|') if movie_data.get('tags') else [],
            earliest_rating=movie_data.get('earliest_rating', ''),
            latest_rating=movie_data.get('latest_rating', ''),
            earliest_tag=movie_data.get('earliest_tag', ''),
            latest_tag=movie_data.get('latest_tag', '')
        )


class GenreMapper:
    """
    Genre Mapper - Application Layer
    """

    @staticmethod
    def to_dto(genre: Genre) -> GenreDto:
        """Convert Genre entity to GenreDto"""
        return GenreDto(
            name=genre.name,
            description=genre.description
        )

    @staticmethod
    def to_dto_list(genres: List[Genre]) -> List[GenreDto]:
        """Convert list of Genre entities to GenreDto list"""
        return [GenreMapper.to_dto(genre) for genre in genres] 