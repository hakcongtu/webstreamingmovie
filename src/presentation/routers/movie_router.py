"""
Movie Router - Presentation Layer
FastAPI routes for movie operations with performance optimizations
"""
import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Path, Query as QueryParam
from fastapi.responses import JSONResponse
from domain.entities.movie import Movie
from application.use_cases.movie_use_cases import MovieUseCase
from application.dtos.movie_schemas import (
    PaginatedResponseDto,
    MovieDetailResponseDto,
    GenreListResponseDto,
    SearchRequestDto,
    ErrorResponseDto,
    SuccessResponseDto,
    MovieDto,
    MovieCreateDto
)
from infrastructure.repositories.sqlite_movie_repository import SqliteMovieRepository

# Create router instance
router = APIRouter(prefix="/api/movies", tags=["movies"])

# Dependency injection for repository and use case
def get_movie_repository() -> SqliteMovieRepository:
    """Dependency to get SQLite movie repository instance"""
    return SqliteMovieRepository()

def get_movie_use_case(
    repository: SqliteMovieRepository = Depends(get_movie_repository)
) -> MovieUseCase:
    """Dependency to get movie use case instance"""
    return MovieUseCase(repository)


@router.get(
    "/",
    response_model=PaginatedResponseDto,
    summary="Get all movies",
    description="Retrieve all movies with pagination support and caching"
)
async def get_movies(
    page: int = QueryParam(1, ge=1, description="Page number"),
    limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get all movies with pagination and caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movies(page=page, limit=limit)
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/{movie_id}",
    response_model=MovieDetailResponseDto,
    summary="Get movie by ID",
    description="Retrieve detailed information about a specific movie including related movies with caching"
)
async def get_movie_by_id(
    movie_id: str = Path(..., description="Movie ID"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movie by ID with related movies and caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movie_by_id(movie_id)
        end_time = time.time()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with ID '{movie_id}' not found"
            )
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/",
    response_model=MovieDto,
    summary="Create a new movie",
    description="Create a new movie with detailed information"
)
async def create_movie(
    movie: MovieCreateDto,
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Create a new movie"""
    return await use_case.create_movie(movie)

@router.get(
    "/search/",
    response_model=PaginatedResponseDto,
    summary="Search movies",
    description="Search movies with various criteria (title, genre, year, etc.) using optimized search indexing"
)
async def search_movies(
    title: Optional[str] = QueryParam(None, description="Search by title"),
    genre: Optional[str] = QueryParam(None, description="Filter by genre"),
    year: Optional[int] = QueryParam(None, description="Filter by year"),
    min_rating: Optional[float] = QueryParam(None, ge=0, le=10, description="Minimum rating"),
    max_rating: Optional[float] = QueryParam(None, ge=0, le=10, description="Maximum rating"),
    page: int = QueryParam(1, ge=1, description="Page number"),
    limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Search movies with criteria using optimized search"""
    try:
        start_time = time.time()
        
        search_request = SearchRequestDto(
            title=title,
            genre=genre,
            year=year,
            min_rating=min_rating,
            max_rating=max_rating,
            page=page,
            limit=limit
        )
        result = await use_case.search_movies(search_request)
        
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        response.headers["X-Search-Criteria"] = f"filters:{len([f for f in [title, genre, year, min_rating, max_rating] if f is not None])}"
        
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/genre/{genre_name}",
    response_model=PaginatedResponseDto,
    summary="Get movies by genre",
    description="Retrieve movies filtered by specific genre with caching"
)
async def get_movies_by_genre(
    genre_name: str = Path(..., description="Genre name"),
    page: int = QueryParam(1, ge=1, description="Page number"),
    limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movies by genre with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movies_by_genre(genre_name, page=page, limit=limit)
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/highly-rated/",
    response_model=PaginatedResponseDto,
    summary="Get highly rated movies",
    description="Retrieve movies with high ratings (4.0+) sorted by rating with caching"
)
async def get_highly_rated_movies(
    page: int = QueryParam(1, ge=1, description="Page number"),
    limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get highly rated movies with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_highly_rated_movies(page=page, limit=limit)
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# @router.get(
#     "/recent/",
#     response_model=PaginatedResponseDto,
#     summary="Get recent movies",
#     description="Retrieve movies sorted by release year (most recent first) with caching"
# )
# async def get_recent_movies(
#     page: int = QueryParam(1, ge=1, description="Page number"),
#     limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
#     use_case: MovieUseCase = Depends(get_movie_use_case)
# ):
#     """Get recent movies by year with caching"""
#     try:
#         start_time = time.time()
#         result = await use_case.get_recent_movies(page=page, limit=limit)
#         end_time = time.time()
        
#         # Add performance header
#         response = JSONResponse(content=result.dict())
#         response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# @router.get(
#     "/popular/",
#     response_model=PaginatedResponseDto,
#     summary="Get popular movies",
#     description="Retrieve movies sorted by ratings count (most popular first) with caching"
# )
# async def get_popular_movies(
#     page: int = QueryParam(1, ge=1, description="Page number"),
#     limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
#     use_case: MovieUseCase = Depends(get_movie_use_case)
# ):
#     """Get popular movies by ratings count with caching"""
#     try:
#         start_time = time.time()
#         result = await use_case.get_popular_movies(page=page, limit=limit)
#         end_time = time.time()
        
#         # Add performance header
#         response = JSONResponse(content=result.dict())
#         response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post(
    "/{movie_id}/view",
    response_model=SuccessResponseDto,
    summary="Increment movie views",
    description="Increment the view count for a specific movie"
)
async def increment_movie_views(
    movie_id: str = Path(..., description="Movie ID"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Increment movie views"""
    try:
        result = await use_case.increment_movie_views(movie_id)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with ID '{movie_id}' not found"
            )
        return SuccessResponseDto(message=f"View count incremented for movie {movie_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/statistics/overview",
    summary="Get movie statistics",
    description="Get overview statistics about movies with caching"
)
async def get_movie_statistics(
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movie statistics with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movie_statistics()
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result)
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/tag/{tag_name}",
    response_model=PaginatedResponseDto,
    summary="Get movies by tag",
    description="Retrieve movies filtered by specific tag with caching"
)
async def get_movies_by_tag(
    tag_name: str = Path(..., description="Tag name"),
    page: int = QueryParam(1, ge=1, description="Page number"),
    limit: int = QueryParam(10, ge=1, le=100, description="Items per page"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movies by tag with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movies_by_tag(tag_name, page=page, limit=limit)
        end_time = time.time()
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/imdb/{imdb_id}",
    response_model=MovieDetailResponseDto,
    summary="Get movie by IMDB ID",
    description="Retrieve movie by IMDB ID with caching"
)
async def get_movie_by_imdb_id(
    imdb_id: str = Path(..., description="IMDB ID"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movie by IMDB ID with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movie_by_imdb_id(imdb_id)
        end_time = time.time()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with IMDB ID '{imdb_id}' not found"
            )
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/tmdb/{tmdb_id}",
    response_model=MovieDetailResponseDto,
    summary="Get movie by TMDB ID",
    description="Retrieve movie by TMDB ID with caching"
)
async def get_movie_by_tmdb_id(
    tmdb_id: str = Path(..., description="TMDB ID"),
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get movie by TMDB ID with caching"""
    try:
        start_time = time.time()
        result = await use_case.get_movie_by_tmdb_id(tmdb_id)
        end_time = time.time()
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Movie with TMDB ID '{tmdb_id}' not found"
            )
        
        # Add performance header
        response = JSONResponse(content=result.dict())
        response.headers["X-Processing-Time"] = f"{end_time - start_time:.3f}s"
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 