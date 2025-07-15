"""
SQLite Movie Repository Implementation - Infrastructure Layer
Implements the IMovieRepository interface using SQLite database
"""
import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
from sqlalchemy.orm import selectinload
import re

from domain.entities.movie import Movie
from domain.entities.genre import Genre
from domain.repositories.movie_repository import IMovieRepository
from domain.value_objects.pagination import PaginationParams, PaginatedResult
from domain.value_objects.search_criteria import SearchCriteria
from infrastructure.database.models import MovieModel, UserModel
from infrastructure.database.database import get_db
from application.mappers.movie_mapper import MovieMapper


class SqliteMovieRepository(IMovieRepository):
    """
    SQLite Movie Repository - Infrastructure Layer
    Implements movie data access using SQLite database
    """

    def __init__(self):
        self._genres_cache: Optional[List[Genre]] = None

    def _movie_model_to_entity(self, model: MovieModel) -> Movie:
        """Convert MovieModel to Movie entity"""
        movie_data = {
            'movieId': str(model.movieId),
            'title': model.title or "",
            'genres': model.genres or "",
            'imdb_id': "",  # Not available in current database
            'tmdb_id': "",  # Not available in current database
            'ratings_count': 0,  # Not available in current database
            'zero_to_one_ratings_count': 0,
            'one_to_two_ratings_count': 0,
            'two_to_three_ratings_count': 0,
            'three_to_four_ratings_count': 0,
            'four_to_five_ratings_count': 0,
            'average_rating': 0.0,  # Not available in current database
            'tags': [],
            'earliest_rating': "",
            'latest_rating': "",
            'earliest_tag': "",
            'latest_tag': ""
        }
        return MovieMapper.from_database_data(movie_data)

    def _entity_to_movie_model(self, movie: Movie) -> MovieModel:
        """Convert Movie entity to MovieModel"""
        return MovieModel(
            movieId=int(movie.movieId) if movie.movieId.isdigit() else 0,
            title=movie.title,
            genres='|'.join(movie.genres)
        )

    def _extract_year_from_title(self, title: str) -> Optional[int]:
        """Extract year from movie title if it ends with (YYYY)."""
        match = re.search(r'\((\d{4})\)\s*$', title)
        if match:
            return int(match.group(1))
        return None

    def _create_movie_data_from_row(self, row) -> dict:
        """Create movie data dictionary from database row"""
        if hasattr(row, '__getitem__'):
            # Handle tuple/row data
            return {
                'movieId': str(row[0]),
                'title': row[1] or "",
                'genres': row[2] or "",
                'imdb_id': row[3] or "",
                'tmdb_id': row[4] or "",
                'ratings_count': row[5] or 0,
                'zero_to_one_ratings_count': row[6] or 0,
                'one_to_two_ratings_count': row[7] or 0,
                'two_to_three_ratings_count': row[8] or 0,
                'three_to_four_ratings_count': row[9] or 0,
                'four_to_five_ratings_count': row[10] or 0,
                'average_rating': row[11] or 0.0,
                'tags': row[12] or "",
                'earliest_rating': row[13] or "",
                'latest_rating': row[14] or "",
                'earliest_tag': row[15] or "",
                'latest_tag': row[16] or ""
            }
        else:
            # Handle SQLAlchemy model object
            return {
                'movieId': str(row.movieId),
                'title': row.title or "",
                'genres': row.genres or "",
                'imdb_id': row.imdb_id or "",
                'tmdb_id': row.tmdb_id or "",
                'ratings_count': row.ratings_count or 0,
                'zero_to_one_ratings_count': row.zero_to_one_ratings_count or 0,
                'one_to_two_ratings_count': row.one_to_two_ratings_count or 0,
                'two_to_three_ratings_count': row.two_to_three_ratings_count or 0,
                'three_to_four_ratings_count': row.three_to_four_ratings_count or 0,
                'four_to_five_ratings_count': row.four_to_five_ratings_count or 0,
                'average_rating': row.average_rating or 0.0,
                'tags': row.tags or "",
                'earliest_rating': row.earliest_rating or "",
                'latest_rating': row.latest_rating or "",
                'earliest_tag': row.earliest_tag or "",
                'latest_tag': row.latest_tag or ""
            }

    async def create(self, movie: Movie) -> Movie:
        """Create a new movie and save to database"""
        async for session in get_db():
            # Convert movieId to int for database
            movie_id = int(movie.movieId) if movie.movieId.isdigit() else 0
            
            # Check for duplicate movieId
            existing = await session.execute(
                select(MovieModel).where(MovieModel.movieId == movie_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Movie with ID {movie.movieId} already exists")
            
            movie_model = self._entity_to_movie_model(movie)
            session.add(movie_model)
            await session.commit()
            await session.refresh(movie_model)
            return movie

    async def find_all(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find all movies with pagination"""
        async for session in get_db():
            # Get total count
            total_count = await session.execute(select(func.count(MovieModel.movieId)))
            total = total_count.scalar()
            
            # Get paginated results - select all available columns
            query = select(MovieModel).offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = []
            for row in result.scalars():
                movie_data = self._create_movie_data_from_row(row)
                movies.append(MovieMapper.from_database_data(movie_data))
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_by_id(self, movie_id: str) -> Optional[Movie]:
        """Find movie by ID"""
        async for session in get_db():
            # Convert movie_id to int for database query
            try:
                movie_id_int = int(movie_id)
            except ValueError:
                return None
                
            result = await session.execute(
                select(MovieModel)
                .where(MovieModel.movieId == movie_id_int)
            )
            row = result.scalar_one_or_none()
            if row:
                movie_data = self._create_movie_data_from_row(row)
                return MovieMapper.from_database_data(movie_data)
            return None

    async def search(
        self, 
        criteria: SearchCriteria, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Search movies based on criteria"""
        async for session in get_db():
            query = select(MovieModel)
            
            # Apply filters
            if criteria.has_title_search():
                query = query.where(
                    MovieModel.title.ilike(f"%{criteria.get_normalized_title()}%")
                )
            
            if criteria.has_genre_filter():
                query = query.where(
                    MovieModel.genres.ilike(f"%{criteria.genre}%")
                )
            
            if criteria.year is not None:
                query = query.where(
                    MovieModel.title.ilike(f"%({criteria.year})%")
                )
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await session.execute(count_query)
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = []
            for row in result.scalars():
                movie_data = self._create_movie_data_from_row(row)
                movies.append(MovieMapper.from_database_data(movie_data))
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_by_genre(
        self, 
        genre: str, 
        pagination: PaginationParams
    ) -> PaginatedResult[Movie]:
        """Find movies by genre"""
        async for session in get_db():
            query = select(MovieModel).where(
                MovieModel.genres.ilike(f"%{genre}%")
            )
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await session.execute(count_query)
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_all_genres(self) -> List[Genre]:
        """Find all unique genres"""
        if self._genres_cache is not None:
            return self._genres_cache

        async for session in get_db():
            result = await session.execute(select(MovieModel.genres))
            genre_strings = result.scalars().all()
            
            genre_set = set()
            for genre_string in genre_strings:
                genres = [g.strip() for g in genre_string.split('|') if g.strip()]
                genre_set.update(genres)
            
            genres = [Genre(name=name) for name in sorted(genre_set)]
            self._genres_cache = genres
            return genres

    async def find_popular(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find popular movies (by ratings count)"""
        async for session in get_db():
            query = select(MovieModel).order_by(desc(MovieModel.ratings_count))
            
            # Get total count
            total_count = await session.execute(select(func.count(MovieModel.movieId)))
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_highly_rated(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find highly rated movies (by average rating)"""
        async for session in get_db():
            query = select(MovieModel).where(
                MovieModel.average_rating >= 4.0
            ).order_by(desc(MovieModel.average_rating))
            
            # Get total count
            total_count = await session.execute(select(func.count(MovieModel.movieId)))
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_recent(self, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find recent movies (by year in title)"""
        async for session in get_db():
            # This is a simplified implementation - in a real scenario,
            # you might want to extract year from title and sort by it
            query = select(MovieModel).order_by(desc(MovieModel.movieId))
            
            # Get total count
            total_count = await session.execute(select(func.count(MovieModel.movieId)))
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def update_views(self, movie_id: str) -> Optional[Movie]:
        """Update movie views (placeholder implementation)"""
        # This is a placeholder - in a real implementation you might
        # want to track views in a separate table
        return await self.find_by_id(movie_id)

    async def get_total_count(self) -> int:
        """Get total number of movies"""
        async for session in get_db():
            result = await session.execute(select(func.count(MovieModel.movieId)))
            return result.scalar()

    async def find_related_movies(self, movie: Movie, limit: int = 5) -> List[Movie]:
        """Find related movies based on genres"""
        async for session in get_db():
            # Convert movie.movieId to int for database query
            try:
                movie_id_int = int(movie.movieId)
            except ValueError:
                movie_id_int = 0
            
            # Find movies with similar genres
            genre_conditions = []
            for genre in movie.genres[:3]:  # Use first 3 genres
                if genre and genre.strip():  # Only add non-empty genres
                    genre_conditions.append(MovieModel.genres.ilike(f"%{genre.strip()}%"))
            
            # Build query based on whether we have genre conditions
            query = select(MovieModel).where(MovieModel.movieId != movie_id_int)
            
            if genre_conditions:
                # Use the | operator for OR conditions
                combined_condition = genre_conditions[0]
                for condition in genre_conditions[1:]:
                    combined_condition = combined_condition | condition
                query = query.where(combined_condition)
            else:
                # If no valid genres, just return some random movies
                query = query.order_by(func.random())
            
            query = query.limit(limit)
            
            result = await session.execute(query)
            return [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]

    async def find_by_tag(self, tag: str, pagination: PaginationParams) -> PaginatedResult[Movie]:
        """Find movies by tag"""
        async for session in get_db():
            query = select(MovieModel).where(
                MovieModel.tags.ilike(f"%{tag}%")
            )
            
            # Get total count
            count_query = select(func.count()).select_from(query.subquery())
            total_count = await session.execute(count_query)
            total = total_count.scalar()
            
            # Apply pagination
            query = query.offset(pagination.offset).limit(pagination.limit)
            result = await session.execute(query)
            movies = [MovieMapper.from_database_data(self._create_movie_data_from_row(m)) for m in result.scalars().all()]
            
            return PaginatedResult(
                data=movies,
                total=total,
                page=pagination.page,
                limit=pagination.limit
            )

    async def find_by_imdb_id(self, imdb_id: str) -> Optional[Movie]:
        """Find movie by IMDB ID"""
        async for session in get_db():
            result = await session.execute(
                select(MovieModel).where(MovieModel.imdb_id == imdb_id)
            )
            movie_model = result.scalar_one_or_none()
            if movie_model:
                return MovieMapper.from_database_data(self._create_movie_data_from_row(movie_model))
            return None

    async def find_by_tmdb_id(self, tmdb_id: str) -> Optional[Movie]:
        """Find movie by TMDB ID"""
        async for session in get_db():
            result = await session.execute(
                select(MovieModel).where(MovieModel.tmdb_id == tmdb_id)
            )
            movie_model = result.scalar_one_or_none()
            if movie_model:
                return MovieMapper.from_database_data(self._create_movie_data_from_row(movie_model))
            return None

    def clear_cache(self):
        """Clear internal cache"""
        self._genres_cache = None 