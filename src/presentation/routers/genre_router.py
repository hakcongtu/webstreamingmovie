"""
Genre Router - Presentation Layer
FastAPI routes for genre operations
"""
from fastapi import APIRouter, HTTPException, Depends

from application.use_cases.movie_use_cases import MovieUseCase
from application.dtos.movie_schemas import GenreListResponseDto
from infrastructure.repositories.sqlite_movie_repository import SqliteMovieRepository

# Create router instance
router = APIRouter(prefix="/api/genres", tags=["genres"])

# Dependency injection for repository and use case
def get_movie_repository() -> SqliteMovieRepository:
    """Dependency to get movie repository instance"""
    return SqliteMovieRepository()

def get_movie_use_case(
    repository: SqliteMovieRepository = Depends(get_movie_repository)
) -> MovieUseCase:
    """Dependency to get movie use case instance"""
    return MovieUseCase(repository)


@router.get(
    "/",
    response_model=GenreListResponseDto,
    summary="Get all genres",
    description="Retrieve all available movie genres"
)
async def get_all_genres(
    use_case: MovieUseCase = Depends(get_movie_use_case)
):
    """Get all available genres"""
    try:
        result = await use_case.get_all_genres()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 