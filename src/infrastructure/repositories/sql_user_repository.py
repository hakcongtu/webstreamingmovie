"""
SQL User Repository Implementation - Infrastructure Layer
Implements the IUserRepository interface using SQLite database
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.database.models import UserModel


class SqlUserRepository(IUserRepository):
    """
    SQL User Repository - Infrastructure Layer
    Implements user data access using SQLite database
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, user_model: UserModel) -> User:
        """Convert database model to domain entity"""
        return User(
            id=user_model.id,
            email=user_model.email,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            full_name=user_model.full_name,
            is_active=user_model.is_active,
            is_superuser=user_model.is_superuser,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            last_login=user_model.last_login
        )

    def _to_model(self, user: User) -> UserModel:
        """Convert domain entity to database model"""
        return UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            hashed_password=user.hashed_password,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )

    async def create_user(self, user: User) -> User:
        """Create a new user"""
        # Check if user ID already exists
        existing_user = await self.find_by_id(user.id)
        if existing_user:
            raise ValueError(f"User with ID {user.id} already exists")
        
        # Check if email already exists
        existing_email = await self.find_by_email(user.email)
        if existing_email:
            raise ValueError(f"User with email {user.email} already exists")
        
        # Check if username already exists
        existing_username = await self.find_by_username(user.username)
        if existing_username:
            raise ValueError(f"User with username {user.username} already exists")
        
        # Create new user model
        user_model = self._to_model(user)
        self.session.add(user_model)
        await self.session.commit()
        await self.session.refresh(user_model)
        
        return self._to_domain(user_model)

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        user_model = result.scalar_one_or_none()
        return self._to_domain(user_model) if user_model else None

    async def update_user(self, updated_user: User) -> User:
        """Update user information"""
        # Check if user exists
        existing_user = await self.find_by_id(updated_user.id)
        if not existing_user:
            raise ValueError(f"User with ID {updated_user.id} not found")
        
        # Update user model
        await self.session.execute(
            update(UserModel)
            .where(UserModel.id == updated_user.id)
            .values(
                email=updated_user.email,
                username=updated_user.username,
                hashed_password=updated_user.hashed_password,
                full_name=updated_user.full_name,
                is_active=updated_user.is_active,
                is_superuser=updated_user.is_superuser,
                updated_at=datetime.utcnow(),
                last_login=updated_user.last_login
            )
        )
        await self.session.commit()
        
        return updated_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            await self.session.delete(user_model)
            await self.session.commit()
            return True
        
        return False

    async def find_all(self) -> List[User]:
        """Get all users"""
        result = await self.session.execute(select(UserModel))
        user_models = result.scalars().all()
        return [self._to_domain(user_model) for user_model in user_models]

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.username == username)
        )
        return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login time"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            user_model.last_login = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(user_model)
            return self._to_domain(user_model)
        
        return None

    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_active == True)
        )
        return len(result.scalars().all())

    async def get_superusers(self) -> List[User]:
        """Get all superusers"""
        result = await self.session.execute(
            select(UserModel).where(UserModel.is_superuser == True)
        )
        user_models = result.scalars().all()
        return [self._to_domain(user_model) for user_model in user_models] 