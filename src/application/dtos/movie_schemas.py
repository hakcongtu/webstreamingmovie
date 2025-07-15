"""
Movie DTOs/Schemas - Application Layer
Pydantic models for data transfer and API documentation
"""
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MovieDto(BaseModel):
    """
    Movie DTO - Complete movie information
    """
    model_config = ConfigDict(from_attributes=True)
    
    movieId: str
    title: str
    genres: List[str]
    imdb_id: str = Field(default="")
    tmdb_id: str = Field(default="")
    ratings_count: int = Field(default=0)
    zero_to_one_ratings_count: int = Field(default=0)
    one_to_two_ratings_count: int = Field(default=0)
    two_to_three_ratings_count: int = Field(default=0)
    three_to_four_ratings_count: int = Field(default=0)
    four_to_five_ratings_count: int = Field(default=0)
    average_rating: float = Field(default=0.0, ge=0, le=10)
    tags: List[str] = Field(default_factory=list)
    earliest_rating: str = Field(default="")
    latest_rating: str = Field(default="")
    earliest_tag: str = Field(default="")
    latest_tag: str = Field(default="")
    is_highly_rated: bool = Field(default=False)
    is_popular: bool = Field(default=False)
    primary_genre: str = Field(default="")
    rating_distribution: dict = Field(default_factory=dict)
    positive_rating_percentage: float = Field(default=0.0)
    negative_rating_percentage: float = Field(default=0.0)
    # rating_trend: str
    


class MovieSummaryDto(BaseModel):
    """
    Movie Summary DTO - Lightweight version for lists
    """
    model_config = ConfigDict(from_attributes=True)
    
    movieId: str
    title: str
    genres: List[str]
    average_rating: float = Field(default=0.0, ge=0, le=10)
    ratings_count: int = Field(default=0)
    tags: List[str] = Field(default_factory=list)
    latest_rating: str = Field(default="")
    is_highly_rated: bool = Field(default=False)
    is_popular: bool = Field(default=False)
    primary_genre: str = Field(default="")
    positive_rating_percentage: float = Field(default=0.0)


class GenreDto(BaseModel):
    """
    Genre DTO
    """
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    description: Optional[str] = None


class PaginationMetaDto(BaseModel):
    """
    Pagination metadata DTO
    """
    page: int = Field(ge=1)
    limit: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    total_pages: int = Field(ge=0)
    has_next: bool
    has_previous: bool


class PaginatedResponseDto(BaseModel):
    """
    Paginated Response DTO - Generic paginated response
    """
    data: List[MovieSummaryDto]
    pagination: PaginationMetaDto

class MovieCreateDto(BaseModel):
    """
    Movie Create DTO
    """
    movieId: str
    title: str
    genres: List[str]
    imdb_id: str
    tmdb_id: str
    ratings_count: int
    zero_to_one_ratings_count: int
    one_to_two_ratings_count: int
    two_to_three_ratings_count: int
    three_to_four_ratings_count: int
    four_to_five_ratings_count: int
    average_rating: float = Field(ge=0, le=10)
    tags: List[str]
    earliest_rating: str
    latest_rating: str
    earliest_tag: str
    latest_tag: str
    
class SearchRequestDto(BaseModel):
    """
    Search Request DTO
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    tag: Optional[str] = Field(None, min_length=1, max_length=50)
    year: Optional[int] = Field(None, ge=1888, le=2030)
    min_rating: Optional[float] = Field(None, ge=0, le=10)
    max_rating: Optional[float] = Field(None, ge=0, le=10)
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)


class MovieDetailResponseDto(BaseModel):
    """
    Movie Detail Response DTO
    """
    movie: MovieDto
    related_movies: List[MovieSummaryDto]


class GenreListResponseDto(BaseModel):
    """
    Genre List Response DTO
    """
    genres: List[GenreDto]
    total: int


class ErrorResponseDto(BaseModel):
    """
    Error Response DTO
    """
    message: str
    detail: Optional[str] = None
    status_code: int


class SuccessResponseDto(BaseModel):
    """
    Success Response DTO
    """
    message: str
    data: Optional[dict] = None


class MovieStatsDto(BaseModel):
    """
    Movie Statistics DTO
    """
    total_movies: int = Field(..., description="Total number of movies")
    total_genres: int = Field(..., description="Total number of genres")
    total_tags: int = Field(..., description="Total number of tags")
    average_rating: float = Field(..., description="Average rating across all movies")
    total_ratings: int = Field(..., description="Total number of ratings")
    highly_rated_movies: int = Field(..., description="Number of highly rated movies (4.0+)")
    popular_movies: int = Field(..., description="Number of popular movies")
    most_popular: List[MovieSummaryDto] = Field(..., description="Most popular movies")
    highest_rated: List[MovieSummaryDto] = Field(..., description="Highest rated movies")
    recent_movies: List[MovieSummaryDto] = Field(..., description="Most recent movies")


class TagDto(BaseModel):
    """
    Tag DTO
    """
    name: str
    count: int = Field(..., description="Number of movies with this tag")


class TagListResponseDto(BaseModel):
    """
    Tag List Response DTO
    """
    tags: List[TagDto]
    total: int 