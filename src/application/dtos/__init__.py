"""
Application DTOs Package
Contains all DTOs/schemas for the movie streaming API
"""

from .movie_schemas import *
from .auth_schemas import *

__all__ = [
    # Movie DTOs
    "MovieDto",
    "MovieSummaryDto",
    "GenreDto",
    "PaginationMetaDto",
    "PaginatedResponseDto",
    "SearchRequestDto",
    "MovieDetailResponseDto",
    "GenreListResponseDto",
    "ErrorResponseDto",
    "SuccessResponseDto",
    "MovieStatsDto",
    "TagDto",
    "TagListResponseDto",
    
    # Auth DTOs
    "UserCreateDto",
    "UserLoginDto",
    "UserResponseDto",
    "TokenResponseDto",
    "TokenPayloadDto",
    "PasswordChangeDto",
    "UserUpdateDto",
    "UserListResponseDto",
    "AuthErrorDto",
    "AuthSuccessDto",
    "RefreshTokenDto",
    "LogoutResponseDto",
    "UserStatsDto"
] 