"""
Authentication Router - Presentation Layer
FastAPI routes for authentication operations
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from application.use_cases.auth_use_cases import AuthUseCase
from application.services.auth_service import AuthService
from application.dtos.auth_schemas import (
    UserCreateDto,
    UserLoginDto,
    UserResponseDto,
    TokenResponseDto,
    UserListResponseDto,
    UserStatsDto,
    AuthSuccessDto,
    LogoutResponseDto,
    GrantSuperuserDto
)
from infrastructure.repositories.sqlite_user_repository import SqliteUserRepository

# Create router instance
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Security scheme - match the one defined in main.py
security = HTTPBearer(scheme_name="bearerAuth")

# Dependency injection for repository, service and use case
def get_user_repository() -> SqliteUserRepository:
    """Dependency to get user repository instance"""
    return SqliteUserRepository()

def get_auth_service() -> AuthService:
    """Dependency to get authentication service instance"""
    return AuthService()

def get_auth_use_case(
    repository: SqliteUserRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service)
) -> AuthUseCase:
    """Dependency to get authentication use case instance"""
    return AuthUseCase(repository, auth_service)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
) -> UserResponseDto:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    user = await auth_use_case.get_current_user(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

async def get_current_superuser(
    current_user: UserResponseDto = Depends(get_current_user)
) -> UserResponseDto:
    """Dependency to ensure current user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


@router.post(
    "/register",
    response_model=AuthSuccessDto,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email, username, password and full name"
)
async def register(
    user_data: UserCreateDto,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Register a new user"""
    try:
        success, message, user_response = await auth_use_case.register_user(user_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        return AuthSuccessDto(
            message=message,
            user=user_response
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenResponseDto,
    summary="User login",
    description="Authenticate user and return access token. Use email or username with password."
)
async def login(
    login_data: UserLoginDto,
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Login user and return access token"""
    try:
        success, message, token_response = await auth_use_case.login_user(login_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=message,
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return token_response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserResponseDto,
    summary="Get current user",
    description="Get information about the currently authenticated user",
    dependencies=[Depends(security)]
)
async def get_me(current_user: UserResponseDto = Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post(
    "/logout",
    response_model=LogoutResponseDto,
    summary="User logout",
    description="Logout current user (invalidate token)",
    dependencies=[Depends(security)]
)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Logout user"""
    try:
        token = credentials.credentials
        # In a simple implementation, we just verify the token
        # In production, you might want to blacklist the token
        user = await auth_use_case.get_current_user(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        return LogoutResponseDto(message="Successfully logged out")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get(
    "/users",
    response_model=UserListResponseDto,
    summary="Get all users",
    description="Get list of all users (superuser only)",
    dependencies=[Depends(security)]
)
async def get_all_users(
    current_user: UserResponseDto = Depends(get_current_superuser),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Get all users (superuser only)"""
    try:
        return await auth_use_case.get_all_users()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.get(
    "/stats",
    response_model=UserStatsDto,
    summary="Get user statistics",
    description="Get user statistics (superuser only)",
    dependencies=[Depends(security)]
)
async def get_user_stats(
    current_user: UserResponseDto = Depends(get_current_superuser),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Get user statistics (superuser only)"""
    try:
        return await auth_use_case.get_user_stats()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.post(
    "/grant-superuser",
    response_model=AuthSuccessDto,
    summary="Grant superuser privileges to a user",
    description="Grant superuser privileges to a user by user ID (admin only)",
    dependencies=[Depends(security)]
)
async def grant_superuser(
    data: GrantSuperuserDto,
    current_user: UserResponseDto = Depends(get_current_superuser),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Grant superuser privileges to a user (admin only)"""
    try:
        success, message, user_response = await auth_use_case.grant_superuser(data.user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        return AuthSuccessDto(
            message=message,
            user=user_response
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Grant superuser failed: {str(e)}"
        )


@router.get(
    "/test-credentials",
    summary="Test credentials",
    description="Get test credentials for demo purposes",
    include_in_schema=True
)
async def get_test_credentials():
    """Get test credentials for demo purposes"""
    return {
        "message": "Test credentials for demo",
        "accounts": {
            "admin": {
                "email": "admin@movieapi.com",
                "username": "admin",
                "password": "admin123",
                "role": "superuser",
                "description": "Full access to all endpoints"
            },
            "demo": {
                "email": "demo@movieapi.com", 
                "username": "demo",
                "password": "demo123",
                "role": "user",
                "description": "Limited access"
            }
        },
        "instructions": [
            "1. Use POST /api/auth/login to get a token",
            "2. Copy the access_token from the response",
            "3. Click the 'Authorize' button (🔒) in Swagger UI",
            "4. Enter: Bearer YOUR_TOKEN_HERE",
            "5. Click 'Authorize'",
            "6. Now you can access protected endpoints"
        ]
    }

@router.get(
    "/debug-token",
    summary="Debug token",
    description="Debug token verification",
    include_in_schema=True,
    dependencies=[Depends(security)]
)
async def debug_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_use_case: AuthUseCase = Depends(get_auth_use_case)
):
    """Debug token verification"""
    try:
        token = credentials.credentials
        print(f"🔍 Debug: Token received: {token[:50]}...")
        
        # Decode token to get payload
        from application.services.auth_service import AuthService
        auth_service = AuthService()
        payload = auth_service.decode_token(token)
        print(f"🔍 Debug: Token payload: {payload}")
        
        # Get user from database
        user = await auth_use_case.get_current_user(token)
        if user:
            print(f"🔍 Debug: User found: {user.email}")
            return {
                "token_valid": True,
                "user_id": user.id,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "user_active": user.is_active,
                "user_can_login": True
            }
        else:
            print("🔍 Debug: User not found")
            return {
                "token_valid": False,
                "error": "User not found in database"
            }
            
    except Exception as e:
        print(f"🔍 Debug: Error: {e}")
        return {
            "token_valid": False,
            "error": str(e)
        } 