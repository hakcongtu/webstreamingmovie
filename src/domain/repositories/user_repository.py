"""
User Repository Interface - Domain Layer
Defines the contract for user data access without implementation details
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.user import User


class IUserRepository(ABC):
    """
    User Repository Interface - Domain Layer
    Defines the contract for user data access without implementation details
    """

    @abstractmethod
    async def create_user(self, user: User) -> User:
        """Create a new user"""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        pass

    @abstractmethod
    async def update_user(self, user: User) -> User:
        """Update user information"""
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    async def find_all(self) -> List[User]:
        """Get all users"""
        pass

    @abstractmethod
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        pass

    @abstractmethod
    async def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login time"""
        pass

    @abstractmethod
    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        pass

    @abstractmethod
    async def get_superusers(self) -> List[User]:
        """Get all superusers"""
        pass 