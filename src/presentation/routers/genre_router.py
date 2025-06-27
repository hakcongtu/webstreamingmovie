"""
Genre Router - Presentation Layer
FastAPI routes for genre operations
"""
from fastapi import APIRouter, HTTPException, Depends

from application.use_cases.movie_use_cases import MovieUseCase
from application.dtos.movie_schemas import GenreListResponseDto
from infrastructure.repositories.csv_movie_repository import CsvMovieRepository

# Create router instance
router = APIRouter(prefix="/api/genres", tags=["genres"])

# Dependency injection for repository and use case
def get_movie_repository() -> CsvMovieRepository:
    """Dependency to get movie repository instance"""
    return CsvMovieRepository()

def get_movie_use_case(
    repository: CsvMovieRepository = Depends(get_movie_repository)
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