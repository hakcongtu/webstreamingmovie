"""
Authentication Use Cases - Application Layer
Orchestrates authentication business logic
"""
from typing import Optional

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository
from application.services.auth_service import AuthService
from application.dtos.auth_schemas import (
    UserCreateDto,
    UserLoginDto,
    UserResponseDto,
    TokenResponseDto,
    UserListResponseDto,
    UserStatsDto,
    AuthErrorDto,
    GrantSuperuserDto,
    TakePrivilegesDto
)


class AuthUseCase:
    """
    Authentication Use Case - Application Layer
    Orchestrates authentication operations
    """

    def __init__(self, user_repository: IUserRepository, auth_service: AuthService):
        self._user_repository = user_repository
        self._auth_service = auth_service

    async def register_user(self, user_data: UserCreateDto) -> tuple[bool, str, Optional[UserResponseDto]]:
        """
        Register a new user
        Returns: (success, message, user_response)
        """
        try:
            # Check if email already exists
            existing_email = await self._user_repository.email_exists(user_data.email)
            if existing_email:
                return False, "Email already registered", None

            # Check if username already exists
            existing_username = await self._user_repository.username_exists(user_data.username)
            if existing_username:
                return False, "Username already taken", None

            # Create user entity
            user = self._auth_service.create_user_from_registration(
                email=user_data.email,
                username=user_data.username,
                password=user_data.password,
                full_name=user_data.full_name
            )

            # Save user to repository
            created_user = await self._user_repository.create_user(user)

            # Convert to response DTO
            user_response = UserResponseDto(
                id=created_user.id,
                email=created_user.email,
                username=created_user.username,
                full_name=created_user.full_name,
                is_active=created_user.is_active,
                is_superuser=created_user.is_superuser,
                created_at=created_user.created_at,
                last_login=created_user.last_login
            )

            return True, "User registered successfully", user_response

        except ValueError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"Registration failed: {str(e)}", None

    async def login_user(self, login_data: UserLoginDto) -> tuple[bool, str, Optional[TokenResponseDto]]:
        """
        Login user and return token
        Returns: (success, message, token_response)
        """
        try:
            # Determine if identifier is email or username
            identifier_type = self._auth_service.is_email_or_username(login_data.email_or_username)
            
            # Find user by email or username
            if identifier_type == "email":
                user = await self._user_repository.find_by_email(login_data.email_or_username)
            else:
                user = await self._user_repository.find_by_username(login_data.email_or_username)

            if not user:
                return False, "Invalid credentials", None

            # Authenticate user
            if not self._auth_service.authenticate_user(user, login_data.password):
                return False, "Invalid credentials", None

            # Update last login
            updated_user = await self._user_repository.update_last_login(user.id)
            if not updated_user:
                updated_user = user

            # Create access token
            access_token, expire_time = self._auth_service.create_access_token(updated_user)

            # Create user response
            user_response = UserResponseDto(
                id=updated_user.id,
                email=updated_user.email,
                username=updated_user.username,
                full_name=updated_user.full_name,
                is_active=updated_user.is_active,
                is_superuser=updated_user.is_superuser,
                created_at=updated_user.created_at,
                last_login=updated_user.last_login
            )

            # Create token response
            token_response = TokenResponseDto(
                access_token=access_token,
                token_type="bearer",
                expires_in=self._auth_service.get_token_expire_time(),
                user=user_response
            )

            return True, "Login successful", token_response

        except Exception as e:
            return False, f"Login failed: {str(e)}", None

    async def get_current_user(self, token: str) -> Optional[UserResponseDto]:
        """
        Get current user from token
        """
        try:
            # Verify token
            token_payload = self._auth_service.verify_token(token)
            if not token_payload:
                return None

            # Get user from repository
            user = await self._user_repository.find_by_id(token_payload.sub)
            if not user or not user.can_login():
                return None

            # Convert to response DTO
            return UserResponseDto(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                last_login=user.last_login
            )

        except Exception:
            return None

    async def get_all_users(self) -> UserListResponseDto:
        """
        Get all users (admin only)
        """
        try:
            users = await self._user_repository.find_all()
            active_count = sum(1 for user in users if user.is_active)
            superuser_count = sum(1 for user in users if user.is_superuser)
            
            user_responses = [
                UserResponseDto(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_superuser=user.is_superuser,
                    created_at=user.created_at,
                    last_login=user.last_login
                )
                for user in users
            ]

            return UserListResponseDto(
                users=user_responses,
                total=len(users),
                active_count=active_count,
                superuser_count=superuser_count
            )

        except Exception:
            return UserListResponseDto(
                users=[],
                total=0,
                active_count=0,
                superuser_count=0
            )

    async def get_user_stats(self) -> UserStatsDto:
        """
        Get user statistics
        """
        try:
            users = await self._user_repository.find_all()
            total_users = len(users)
            active_users = sum(1 for user in users if user.is_active)
            inactive_users = total_users - active_users
            superusers = sum(1 for user in users if user.is_superuser)
            
            # Calculate recent registrations (last 30 days)
            from datetime import datetime, timedelta
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_registrations = sum(
                1 for user in users if user.created_at >= thirty_days_ago
            )

            return UserStatsDto(
                total_users=total_users,
                active_users=active_users,
                inactive_users=inactive_users,
                superusers=superusers,
                recent_registrations=recent_registrations
            )

        except Exception:
            return UserStatsDto(
                total_users=0,
                active_users=0,
                inactive_users=0,
                superusers=0,
                recent_registrations=0
            ) 

    async def grant_superuser(self, user_id: str) -> tuple[bool, str, Optional[UserResponseDto]]:
        """
        Grant superuser privileges to a user by user_id
        Returns: (success, message, user_response)
        """
        try:
            user = await self._user_repository.find_by_id(user_id)
            if not user:
                return False, "User not found", None
            if user.is_superuser:
                return False, "User is already a superuser", None
            updated_user = user.make_superuser()
            updated_user = await self._user_repository.update_user(updated_user)
            user_response = UserResponseDto(
                id=updated_user.id,
                email=updated_user.email,
                username=updated_user.username,
                full_name=updated_user.full_name,
                is_active=updated_user.is_active,
                is_superuser=updated_user.is_superuser,
                created_at=updated_user.created_at,
                last_login=updated_user.last_login
            )
            return True, "Superuser privileges granted", user_response
        except Exception as e:
            return False, f"Failed to grant superuser: {str(e)}", None 
        
    async def take_privileges(self, user_id: str) -> tuple[bool, str, Optional[UserResponseDto]]:
        """
        Take superuser privileges from a user by user_id
        Returns: (success, message, user_response)
        """
        try:
            user = await self._user_repository.find_by_id(user_id)
            if not user:
                return False, "User not found", None
            if not user.is_superuser:
                return False, "User is not a superuser", None
            updated_user = user.make_user()
            updated_user = await self._user_repository.update_user(updated_user)
            user_response = UserResponseDto(
                id=updated_user.id,
                email=updated_user.email,
                username=updated_user.username,
                full_name=updated_user.full_name,
                is_active=updated_user.is_active,
                is_superuser=updated_user.is_superuser,
                created_at=updated_user.created_at,
                last_login=updated_user.last_login
            )
            return True, "Superuser privileges taken", user_response
        except Exception as e:
            return False, f"Failed to take privileges: {str(e)}", None