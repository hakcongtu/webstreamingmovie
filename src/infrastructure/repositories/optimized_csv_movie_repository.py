"""
Optimized CSV Movie Repository Implementation - Infrastructure Layer
High-performance implementation with caching and async I/O
"""
import csv
import os
import asyncio
import aiofiles
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
import re
import logging
from functools import lru_cache

from domain.entities.movie import Movie
from domain.entities.genre import Genre
from domain.repositories.movie_repository import IMovieRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from domain.value_objects.search_criteria import SearchCriteria
from infrastructure.cache.cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


class OptimizedCsvMovieRepository(IMovieRepository):
    """
    Optimized CSV Movie Repository - Infrastructure Layer
    High-performance implementation with caching and async I/O
    """

    def __init__(self, csv_file_path: str = "data/movies.csv"):
        self.csv_file_path = csv_file_path
        self._movies_cache: Optional[List[Movie]] = None
        self._genres_cache: Optional[List[Genre]] = None
        self._search_index: Optional[Dict[str, List[int]]] = None
        self._cache_manager = None
        self._last_modified = 0
        self._lock = asyncio.Lock()

    async def _get_cache_manager(self):
        """Get cache manager instance"""
        if self._cache_manager is None:
            self._cache_manager = await get_cache_manager()
        return self._cache_manager

    async def _get_file_modified_time(self) -> float:
        """Get file modification time"""
        try:
            stat = os.stat(self.csv_file_path)
            return stat.st_mtime
        except OSError:
            return 0

    async def _should_reload_cache(self) -> bool:
        """Check if cache should be reloaded"""
        if self._movies_cache is None:
            return True
        
        current_modified = await self._get_file_modified_time()
        return current_modified > self._last_modified

    async def _load_movies_async(self) -> List[Movie]:
        """Load movies from CSV file asynchronously with caching"""
        # Check cache first
        cache_manager = await self._get_cache_manager()
        cache_key = f"movies_data_{self.csv_file_path}"
        
        cached_data = await cache_manager.get(cache_key)
        if cached_data and not await self._should_reload_cache():
            self._movies_cache = cached_data
            return cached_data

        async with self._lock:
            # Double-check after acquiring lock
            if self._movies_cache is not None and not await self._should_reload_cache():
                return self._movies_cache

            if not os.path.exists(self.csv_file_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")

            movies = []
            try:
                # Use pandas for faster CSV reading
                logger.info(f"Loading movies from CSV: {self.csv_file_path}")
                df = pd.read_csv(self.csv_file_path)
                
                logger.info(f"CSV loaded: {len(df)} rows, {len(df.columns)} columns")
                
                # Process in chunks for better memory usage
                chunk_size = 1000
                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i:i + chunk_size]
                    
                    for _, row in chunk.iterrows():
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
            self._last_modified = await self._get_file_modified_time()
            
            # Cache the data
            await cache_manager.set(cache_key, movies, ttl=1800)  # 30 minutes
            
            logger.info(f"✅ Loaded {len(movies)} movies from CSV")
            return movies

    async def _build_search_index(self, movies: List[Movie]) -> Dict[str, List[int]]:
        """Build search index for faster lookups"""
        if self._search_index is not None:
            return self._search_index

        index = {
            'title_lower': {},
            'genre': {},
            'year': {},
            'country': {},
            'language': {},
            'status': {},
            'tags': {}
        }

        for i, movie in enumerate(movies):
            # Title index
            title_lower = movie.title.lower()
            for word in title_lower.split():
                if word not in index['title_lower']:
                    index['title_lower'][word] = []
                index['title_lower'][word].append(i)

            # Genre index
            for genre in movie.genres:
                if genre not in index['genre']:
                    index['genre'][genre] = []
                index['genre'][genre].append(i)

            # Tags index
            for tag in movie.tags:
                if tag not in index['tags']:
                    index['tags'][tag] = []
                index['tags'][tag].append(i)

        self._search_index = index
        return index

    async def _load_genres(self) -> List[Genre]:
        """Load unique genres from movies with caching"""
        cache_manager = await self._get_cache_manager()
        cache_key = "genres_list"
        
        cached_genres = await cache_manager.get(cache_key)
        if cached_genres:
            self._genres_cache = cached_genres
            return cached_genres

        movies = await self._load_movies_async()
        genre_set = set()
        
        for movie in movies:
            for genre_name in movie.genres:
                genre_set.add(genre_name.strip())
        
        genres = [Genre(name=name) for name in sorted(genre_set)]
        self._genres_cache = genres
        
        # Cache genres
        await cache_manager.set(cache_key, genres, ttl=3600)  # 1 hour
        
        return genres

    def _apply_pagination(
        self, 
        movies: List[Movie], 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Apply pagination to movie list"""
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

    def _extract_year_from_title(self, title: str) -> Optional[int]:
        """Extract year from movie title if it ends with (YYYY)"""
        match = re.search(r'\((\d{4})\)\s*$', title)
        if match:
            return int(match.group(1))
        return None

    async def _filter_movies_optimized(
        self, 
        movies: List[Movie], 
        criteria: SearchCriteria
    ) -> List[Movie]:
        """Optimized movie filtering using search index"""
        if not criteria.has_any_filters():
            return movies

        # Build search index if not exists
        search_index = await self._build_search_index(movies)
        
        # Get candidate indices
        candidate_indices = set(range(len(movies)))
        
        if criteria.has_title_search():
            title_words = criteria.get_normalized_title().split()
            title_candidates = set()
            for word in title_words:
                if word in search_index['title_lower']:
                    if not title_candidates:
                        title_candidates = set(search_index['title_lower'][word])
                    else:
                        title_candidates &= set(search_index['title_lower'][word])
            if title_candidates:
                candidate_indices &= title_candidates

        if criteria.has_genre_filter():
            if criteria.genre in search_index['genre']:
                genre_candidates = set(search_index['genre'][criteria.genre])
                candidate_indices &= genre_candidates
            else:
                return []

        # Apply remaining filters
        filtered_movies = []
        for idx in candidate_indices:
            movie = movies[idx]
            
            if criteria.year is not None:
                movie_year = self._extract_year_from_title(movie.title)
                if movie_year != criteria.year:
                    continue

            if criteria.min_rating is not None and movie.average_rating < criteria.min_rating:
                continue

            if criteria.max_rating is not None and movie.average_rating > criteria.max_rating:
                continue

            filtered_movies.append(movie)

        return filtered_movies

    async def find_all(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find all movies with pagination"""
        movies = await self._load_movies_async()
        return self._apply_pagination(movies, pagination)

    async def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """Find movie by ID with caching"""
        cache_manager = await self._get_cache_manager()
        cache_key = f"movie_id_{movie_id}"
        
        cached_movie = await cache_manager.get(cache_key)
        if cached_movie:
            return cached_movie

        movies = await self._load_movies_async()
        
        for movie in movies:
            if movie.movieId == movie_id:
                # Cache individual movie
                await cache_manager.set(cache_key, movie, ttl=1800)  # 30 minutes
                return movie
        
        return None

    async def search(
        self, 
        criteria: SearchCriteria, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Search movies with optimized filtering"""
        movies = await self._load_movies_async()
        filtered_movies = await self._filter_movies_optimized(movies, criteria)
        return self._apply_pagination(filtered_movies, pagination)

    async def find_by_genre(
        self, 
        genre: str, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Find movies by genre with caching"""
        cache_manager = await self._get_cache_manager()
        cache_key = f"genre_{genre}_{pagination.page}_{pagination.limit}"
        
        cached_result = await cache_manager.get(cache_key)
        if cached_result:
            return PaginatedResult(**cached_result)

        movies = await self._load_movies_async()
        search_index = await self._build_search_index(movies)
        
        if genre in search_index['genre']:
            genre_movies = [movies[i] for i in search_index['genre'][genre]]
            result = self._apply_pagination(genre_movies, pagination)
        else:
            result = PaginatedResult(data=[], total=0, page=pagination.page, limit=pagination.limit)

        # Cache result
        await cache_manager.set(cache_key, result.dict(), ttl=900)  # 15 minutes
        
        return result

    async def find_all_genres(self) -> List[Genre]:
        """Find all genres with caching"""
        return await self._load_genres()

    async def find_popular(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find popular movies by ratings count"""
        movies = await self._load_movies_async()
        sorted_movies = sorted(movies, key=lambda m: m.ratings_count, reverse=True)
        return self._apply_pagination(sorted_movies, pagination)

    async def find_highly_rated(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find highly rated movies"""
        movies = await self._load_movies_async()
        highly_rated = [m for m in movies if m.average_rating >= 4.0]
        sorted_movies = sorted(highly_rated, key=lambda m: m.average_rating, reverse=True)
        return self._apply_pagination(sorted_movies, pagination)

    async def find_recent(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find recent movies by year"""
        movies = await self._load_movies_async()
        
        # Extract years and sort
        movies_with_years = []
        for movie in movies:
            year = self._extract_year_from_title(movie.title)
            if year:
                movies_with_years.append((movie, year))
        
        sorted_movies = [m[0] for m in sorted(movies_with_years, key=lambda x: x[1], reverse=True)]
        return self._apply_pagination(sorted_movies, pagination)

    async def update_views(self, movie_id: str) -> Optional[Movie]:
        """Update movie views (placeholder for future implementation)"""
        # This would typically update a view count in the database
        # For now, just return the movie
        return await self.find_by_id(movie_id)

    async def get_total_count(self) -> int:
        """Get total movie count with caching"""
        cache_manager = await self._get_cache_manager()
        cache_key = "total_movie_count"
        
        cached_count = await cache_manager.get(cache_key)
        if cached_count is not None:
            return cached_count

        movies = await self._load_movies_async()
        count = len(movies)
        
        # Cache count
        await cache_manager.set(cache_key, count, ttl=3600)  # 1 hour
        
        return count

    async def find_related_movies(self, movie: Movie, limit: int = 5) -> List[Movie]:
        """Find related movies based on genres"""
        movies = await self._load_movies_async()
        
        # Find movies with similar genres
        related = []
        for other_movie in movies:
            if other_movie.movieId != movie.movieId:
                common_genres = set(movie.genres) & set(other_movie.genres)
                if common_genres:
                    related.append((other_movie, len(common_genres)))
        
        # Sort by number of common genres and rating
        related.sort(key=lambda x: (x[1], x[0].average_rating), reverse=True)
        
        return [movie for movie, _ in related[:limit]]

    async def find_by_tag(self, tag: str, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find movies by tag"""
        movies = await self._load_movies_async()
        search_index = await self._build_search_index(movies)
        
        if tag in search_index['tags']:
            tag_movies = [movies[i] for i in search_index['tags'][tag]]
            return self._apply_pagination(tag_movies, pagination)
        else:
            return PaginatedResult(data=[], total=0, page=pagination.page, limit=pagination.limit)

    async def find_by_imdb_id(self, imdb_id: str) -> Optional[Movie]:
        """Find movie by IMDB ID"""
        movies = await self._load_movies_async()
        
        for movie in movies:
            if movie.imdb_id == imdb_id:
                return movie
        
        return None

    async def find_by_tmdb_id(self, tmdb_id: str) -> Optional[Movie]:
        """Find movie by TMDB ID"""
        movies = await self._load_movies_async()
        
        for movie in movies:
            if movie.tmdb_id == tmdb_id:
                return movie
        
        return None

    def clear_cache(self):
        """Clear all caches"""
        self._movies_cache = None
        self._genres_cache = None
        self._search_index = None
        self._last_modified = 0

    # Backward compatibility - keep the old class name
    class OptimizedCsvMovieRepository(OptimizedParquetMovieRepository):
        """Backward compatibility alias"""
        pass 