"""
CSV Movie Repository Implementation - Infrastructure Layer
Implements the IMovieRepository interface using CSV file as data source
"""
import csv
import os
import asyncio
from typing import List, Optional
import pandas as pd
from datetime import datetime
import re

from domain.entities.movie import Movie
from domain.entities.genre import Genre
from domain.repositories.movie_repository import IMovieRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from domain.value_objects.search_criteria import SearchCriteria


class CsvMovieRepository(IMovieRepository):
    """
    CSV Movie Repository - Infrastructure Layer
    Implements movie data access using CSV file
    """

    def __init__(self, csv_file_path: str = "data/movies.csv"):
        self.csv_file_path = csv_file_path
        self._movies_cache: Optional[List[Movie]] = None
        self._genres_cache: Optional[List[Genre]] = None

    async def _load_movies(self) -> List[Movie]:
        """(Private) Load movies from CSV file with caching. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        if self._movies_cache is not None:
            return self._movies_cache

        if not os.path.exists(self.csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

        movies = []
        try:
            df = pd.read_csv(self.csv_file_path)
            df.to_parquet(self.csv_file_path.replace('.csv', '.parquet'))
            df = pd.read_parquet(self.csv_file_path.replace('.csv', '.parquet'),engine='pyarrow')
            
            for _, row in df.iterrows():
                # Parse genres and tags from pipe-separated strings
                genres = [g.strip() for g in str(row['genres']).split('|') if g.strip()]
                tags = [t.strip() for t in str(row['tags']).split('|') if t.strip()]
                
                movie = Movie(
                    movieId=str(row['movieId']),
                    title=str(row['title']),
                    genres=genres,
                    imdb_id=str(row['imdb_id']),
                    tmdb_id=str(row['tmdb_id']),
                    ratings_count=int(row['ratings_count']),
                    zero_to_one_ratings_count=int(row['zero_to_one_ratings_count']),
                    one_to_two_ratings_count=int(row['one_to_two_ratings_count']),
                    two_to_three_ratings_count=int(row['two_to_three_ratings_count']),
                    three_to_four_ratings_count=int(row['three_to_four_ratings_count']),
                    four_to_five_ratings_count=int(row['four_to_five_ratings_count']),
                    average_rating=float(row['average_rating']),
                    tags=tags,
                    earliest_rating=str(row['earliest_rating']),
                    latest_rating=str(row['latest_rating']),
                    earliest_tag=str(row['earliest_tag']),
                    latest_tag=str(row['latest_tag'])
                )
                movies.append(movie)
                
        except Exception as e:
            raise ValueError(f"Error loading movies from CSV: {str(e)}")

        self._movies_cache = movies
        return movies

    async def _load_genres(self) -> List[Genre]:
        """(Private) Load unique genres from movies. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        if self._genres_cache is not None:
            return self._genres_cache

        movies = await self._load_movies()
        genre_set = set()
        
        for movie in movies:
            for genre_name in movie.genres:
                genre_set.add(genre_name.strip())
        
        genres = [Genre(name=name) for name in sorted(genre_set)]
        self._genres_cache = genres
        return genres

    def _apply_pagination(
        self, 
        movies: List[Movie], 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """(Private) Apply pagination to movie list. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        total = len(movies)
        start_idx = pagination.offset
        end_idx = start_idx + pagination.limit
        
        paginated_movies = movies[start_idx:end_idx]
        
        return PaginatedResult(
            data=paginated_movies,
            total=total,
            page=pagination.page,
            limit=pagination.limit
        )
    
    def _create_movie(self, movie: Movie) -> Movie:
        """(Private) Create a new movie. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        return Movie(
            movieId=movie.movieId,
            title=movie.title,
            genres=movie.genres,
            imdb_id=movie.imdb_id,
            tmdb_id=movie.tmdb_id,
            tags=movie.tags,
            earliest_rating=movie.earliest_rating,
            latest_rating=movie.latest_rating,
            earliest_tag=movie.earliest_tag,
            latest_tag=movie.latest_tag,
            average_rating=movie.average_rating,
            ratings_count=movie.ratings_count,
            zero_to_one_ratings_count=movie.zero_to_one_ratings_count,
            one_to_two_ratings_count=movie.one_to_two_ratings_count,
            two_to_three_ratings_count=movie.two_to_three_ratings_count,
            three_to_four_ratings_count=movie.three_to_four_ratings_count,
            four_to_five_ratings_count=movie.four_to_five_ratings_count
        )

    async def _save_movies(self, movies: List[Movie]) -> None:
        """(Private) Save movies to CSV file. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        fieldnames = [
            'movieId', 'title', 'genres', 'imdb_id', 'tmdb_id',
            'ratings_count', 'zero_to_one_ratings_count', 'one_to_two_ratings_count',
            'two_to_three_ratings_count', 'three_to_four_ratings_count', 'four_to_five_ratings_count',
            'average_rating', 'tags', 'earliest_rating', 'latest_rating', 'earliest_tag', 'latest_tag'
        ]
        with open(self.csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for movie in movies:
                writer.writerow({
                    'movieId': movie.movieId,
                    'title': movie.title,
                    'genres': '|'.join(movie.genres),
                    'imdb_id': movie.imdb_id,
                    'tmdb_id': movie.tmdb_id,
                    'ratings_count': movie.ratings_count,
                    'zero_to_one_ratings_count': movie.zero_to_one_ratings_count,
                    'one_to_two_ratings_count': movie.one_to_two_ratings_count,
                    'two_to_three_ratings_count': movie.two_to_three_ratings_count,
                    'three_to_four_ratings_count': movie.three_to_four_ratings_count,
                    'four_to_five_ratings_count': movie.four_to_five_ratings_count,
                    'average_rating': movie.average_rating,
                    'tags': '|'.join(movie.tags),
                    'earliest_rating': movie.earliest_rating,
                    'latest_rating': movie.latest_rating,
                    'earliest_tag': movie.earliest_tag,
                    'latest_tag': movie.latest_tag
                })

    async def create(self, movie: Movie) -> Movie:
        """Create a new movie and save to CSV"""
        movies = await self._load_movies()
        # Check for duplicate movieId
        if any(m.movieId == movie.movieId for m in movies):
            raise ValueError(f"Movie with ID {movie.movieId} already exists")
        movies.append(movie)
        await self._save_movies(movies)
        self._movies_cache = movies
        return movie

    def _extract_year_from_title(self, title: str) -> Optional[int]:
        """(Private) Extract year from movie title if it ends with (YYYY)."""
        match = re.search(r'\((\d{4})\)\s*$', title)
        if match:
            return int(match.group(1))
        return None

    def _filter_movies(self, movies: List[Movie], criteria: SearchCriteria) -> List[Movie]:
        """(Private) Filter movies based on search criteria. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        filtered = movies

        if criteria.has_title_search():
            filtered = [
                m for m in filtered 
                if criteria.get_normalized_title() in m.title.lower()
            ]

        if criteria.has_genre_filter():
            filtered = [
                m for m in filtered 
                if m.has_genre(criteria.genre)
            ]

        if criteria.year is not None:
            filtered = [
                m for m in filtered
                if self._extract_year_from_title(m.title) == criteria.year
            ]

        if criteria.country is not None:
            filtered = [
                m for m in filtered 
                if any(criteria.get_normalized_country() in tag.lower() for tag in m.tags)
            ]

        if criteria.language is not None:
            filtered = [
                m for m in filtered 
                if any(criteria.get_normalized_language() in tag.lower() for tag in m.tags)
            ]

        # if criteria.status is not None:
        #     filtered = [
        #         m for m in filtered 
        #         if criteria.get_normalized_status() in m.get_rating_trend().lower()
        #     ]

        if criteria.min_rating is not None:
            filtered = [m for m in filtered if m.average_rating >= criteria.min_rating]

        if criteria.max_rating is not None:
            filtered = [m for m in filtered if m.average_rating <= criteria.max_rating]

        return filtered

    async def find_all(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get all movies with pagination"""
        movies = await self._load_movies()
        return self._apply_pagination(movies, pagination)

    async def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """Find movie by ID"""
        movies = await self._load_movies()
        for movie in movies:
            if movie.movieId == movie_id:
                return movie
        return None

    async def search(
        self, 
        criteria: SearchCriteria, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Search movies with criteria and pagination"""
        movies = await self._load_movies()
        filtered_movies = self._filter_movies(movies, criteria)
        return self._apply_pagination(filtered_movies, pagination)

    async def find_by_genre(
        self, 
        genre: str, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Get movies by genre with pagination"""
        movies = await self._load_movies()
        filtered_movies = [m for m in movies if m.has_genre(genre)]
        return self._apply_pagination(filtered_movies, pagination)

    async def find_all_genres(self) -> List[Genre]:
        """Get all available genres"""
        return await self._load_genres()

    async def find_popular(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get popular movies (by ratings count) with pagination"""
        movies = await self._load_movies()
        sorted_movies = sorted(movies, key=lambda m: m.ratings_count, reverse=True)
        return self._apply_pagination(sorted_movies, pagination)

    async def find_highly_rated(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get highly rated movies with pagination"""
        movies = await self._load_movies()
        # Filter movies with rating >= 4.0 and sort by rating
        highly_rated = [m for m in movies if m.is_highly_rated()]
        sorted_movies = sorted(highly_rated, key=lambda m: m.average_rating, reverse=True)
        return self._apply_pagination(sorted_movies, pagination)

    async def find_recent(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get recent movies with pagination"""
        movies = await self._load_movies()
        # Sort by latest rating date (most recent first)
        sorted_movies = sorted(
            movies, 
            key=lambda m: m.latest_rating, 
            reverse=True
        )
        return self._apply_pagination(sorted_movies, pagination)

    async def update_views(self, movie_id: str) -> Optional[Movie]:
        """Update movie view count (simulation - not applicable for this data structure)"""
        # Note: This is a simulation since we don't have views in the new structure
        # In a real implementation, you might track this separately or update ratings_count
        movie = await self.find_by_id(movie_id)
        return movie  # Return the same movie since we can't update views

    async def get_total_count(self) -> int:
        """Get total count of movies"""
        movies = await self._load_movies()
        return len(movies)

    async def find_related_movies(self, movie: Movie, limit: int = 5) -> List[Movie]:
        """Find movies related to the given movie (same genres)"""
        movies = await self._load_movies()
        related = []
        
        for m in movies:
            if m.movieId != movie.movieId:  # Exclude the movie itself
                # Check if movies share at least one genre
                shared_genres = set(movie.genres) & set(m.genres)
                if shared_genres:
                    related.append(m)
        
        # Sort by average rating and return limited results
        related.sort(key=lambda m: m.average_rating, reverse=True)
        return related[:limit]

    async def find_by_tag(self, tag: str, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Get movies by tag with pagination"""
        movies = await self._load_movies()
        filtered_movies = [m for m in movies if m.has_tag(tag)]
        return self._apply_pagination(filtered_movies, pagination)

    async def find_by_imdb_id(self, imdb_id: str) -> Optional[Movie]:
        """Find movie by IMDB ID"""
        movies = await self._load_movies()
        for movie in movies:
            if movie.imdb_id == imdb_id:
                return movie
        return None

    async def find_by_tmdb_id(self, tmdb_id: str) -> Optional[Movie]:
        """Find movie by TMDB ID"""
        movies = await self._load_movies()
        for movie in movies:
            if movie.tmdb_id == tmdb_id:
                return movie
        return None

    def clear_cache(self):
        """Clear the movies and genres cache (dùng khi cần reload dữ liệu từ file)"""
        self._movies_cache = None
        self._genres_cache = None 