"""
User Entity - Domain Model
Represents the user entity for authentication and authorization
"""
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
import re


@dataclass(frozen=True)
class User:
    """
    User Entity - Immutable domain object
    Contains user information and business logic
    """
    id: str
    email: str
    username: str
    hashed_password: str
    full_name: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    def __post_init__(self):
        """Domain validation rules"""
        self._validate()

    def _validate(self) -> None:
        """Validate domain rules"""
        if not self.id or not self.id.strip():
            raise ValueError("User ID cannot be empty")
        
        if not self.email or not self.email.strip():
            raise ValueError("Email cannot be empty")
        
        if not self._is_valid_email(self.email):
            raise ValueError("Invalid email format")
        
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty")
        
        if not self._is_valid_username(self.username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        if not self.hashed_password:
            raise ValueError("Hashed password cannot be empty")
        
        if not self.full_name or not self.full_name.strip():
            raise ValueError("Full name cannot be empty")
        
    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def _is_valid_username(self, username: str) -> bool:
        """Validate username format (alphanumeric and underscore only)"""
        username_pattern = r'^[a-zA-Z0-9_]+$'
        return re.match(username_pattern, username) is not None

    def is_admin(self) -> bool:
        """Business logic: Check if user is admin"""
        return self.is_superuser

    def can_access_admin_features(self) -> bool:
        """Business logic: Check if user can access admin features"""
        return self.is_active and self.is_superuser

    def can_login(self) -> bool:
        """Business logic: Check if user can login"""
        return self.is_active

    def get_display_name(self) -> str:
        """Business logic: Get user's display name"""
        return self.full_name if self.full_name else self.username

    def update_last_login(self) -> 'User':
        """Business logic: Create new instance with updated last login time"""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=self.is_superuser,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            last_login=datetime.utcnow()
        )

    def activate(self) -> 'User':
        """Business logic: Activate user account"""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=True,
            is_superuser=self.is_superuser,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            last_login=self.last_login
        )

    def deactivate(self) -> 'User':
        """Business logic: Deactivate user account"""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=False,
            is_superuser=self.is_superuser,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            last_login=self.last_login
        )

    def make_superuser(self) -> 'User':
        """Business logic: Grant superuser privileges"""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=True,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            last_login=self.last_login
        )
    
    def make_user(self) -> 'User':
        """Business logic: Take superuser privileges"""
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            full_name=self.full_name,
            is_active=self.is_active,
            is_superuser=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            last_login=self.last_login
        )