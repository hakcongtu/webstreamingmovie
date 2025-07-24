"""
Authentication DTOs/Schemas - Application Layer
Pydantic models for authentication data transfer and API documentation
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreateDto(BaseModel):
    """
    User Registration DTO
    """
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    password: str = Field(..., min_length=6, max_length=100, description="Password (minimum 6 characters)")
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name")


class UserLoginDto(BaseModel):
    """
    User Login DTO
    """
    email_or_username: str = Field(..., description="Email address or username")
    password: str = Field(..., description="Password")


class UserResponseDto(BaseModel):
    """
    User Response DTO - Public user information
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    username: str
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class TokenResponseDto(BaseModel):
    """
    Token Response DTO
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponseDto = Field(..., description="User information")


class TokenPayloadDto(BaseModel):
    """
    Token Payload DTO - Internal use for JWT
    """
    sub: str = Field(..., description="Subject (user ID)")
    email: str = Field(..., description="User email")
    username: str = Field(..., description="Username")
    is_superuser: bool = Field(default=False, description="Is superuser")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")


class PasswordChangeDto(BaseModel):
    """
    Password Change DTO
    """
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=6, max_length=100, description="New password (minimum 6 characters)")


class UserUpdateDto(BaseModel):
    """
    User Update DTO
    """
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")


class UserListResponseDto(BaseModel):
    """
    User List Response DTO
    """
    users: list[UserResponseDto]
    total: int
    active_count: int
    superuser_count: int


class AuthErrorDto(BaseModel):
    """
    Authentication Error DTO
    """
    message: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    detail: Optional[str] = Field(None, description="Detailed error information")


class AuthSuccessDto(BaseModel):
    """
    Authentication Success DTO
    """
    message: str = Field(..., description="Success message")
    user: Optional[UserResponseDto] = Field(None, description="User information")


class RefreshTokenDto(BaseModel):
    """
    Refresh Token DTO
    """
    refresh_token: str = Field(..., description="Refresh token")


class LogoutResponseDto(BaseModel):
    """
    Logout Response DTO
    """
    message: str = Field(default="Successfully logged out")


class UserStatsDto(BaseModel):
    """
    User Statistics DTO
    """
    total_users: int = Field(..., description="Total number of users")
    active_users: int = Field(..., description="Number of active users")
    inactive_users: int = Field(..., description="Number of inactive users")
    superusers: int = Field(..., description="Number of superusers")
    recent_registrations: int = Field(..., description="Registrations in last 30 days") 


class GrantSuperuserDto(BaseModel):
    """
    Grant Superuser DTO
    """
    user_id: str = Field(..., description="User ID to grant superuser privileges") 
    
class TakePrivilegesDto(BaseModel):
    """
    Take Privileges DTO
    """
    user_id: str = Field(..., description="User ID to take privileges") 