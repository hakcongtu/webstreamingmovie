"""
SQLite User Repository Implementation - Infrastructure Layer
Implements the IUserRepository interface using SQLite database
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from passlib.context import CryptContext

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.database.models import UserModel
from infrastructure.database.database import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SqliteUserRepository(IUserRepository):
    """
    SQLite User Repository - Infrastructure Layer
    Implements user data access using SQLite database
    """

    def _user_model_to_entity(self, model: UserModel) -> User:
        """Convert UserModel to User entity"""
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            is_active=model.is_active,
            is_superuser=model.is_superuser,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )

    def _entity_to_user_model(self, user: User) -> UserModel:
        """Convert User entity to UserModel"""
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
        async for session in get_db():
            # Check for duplicate email or username
            existing_email = await session.execute(
                select(UserModel).where(UserModel.email == user.email)
            )
            if existing_email.scalar_one_or_none():
                raise ValueError(f"User with email {user.email} already exists")
            
            existing_username = await session.execute(
                select(UserModel).where(UserModel.username == user.username)
            )
            if existing_username.scalar_one_or_none():
                raise ValueError(f"User with username {user.username} already exists")
            
            user_model = self._entity_to_user_model(user)
            session.add(user_model)
            await session.commit()
            await session.refresh(user_model)
            return user

    async def create(self, user: User) -> User:
        """Create a new user (alias for create_user)"""
        return await self.create_user(user)

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            if user_model:
                return self._user_model_to_entity(user_model)
            return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            user_model = result.scalar_one_or_none()
            if user_model:
                return self._user_model_to_entity(user_model)
            return None

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            user_model = result.scalar_one_or_none()
            if user_model:
                return self._user_model_to_entity(user_model)
            return None

    async def update_user(self, user: User) -> User:
        """Update user"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.id == user.id)
            )
            user_model = result.scalar_one_or_none()
            if not user_model:
                raise ValueError(f"User with ID {user.id} not found")
            
            # Update fields
            user_model.email = user.email
            user_model.username = user.username
            user_model.hashed_password = user.hashed_password
            user_model.full_name = user.full_name
            user_model.is_active = user.is_active
            user_model.is_superuser = user.is_superuser
            user_model.updated_at = user.updated_at
            user_model.last_login = user.last_login
            
            await session.commit()
            await session.refresh(user_model)
            return self._user_model_to_entity(user_model)

    async def update(self, user: User) -> User:
        """Update user (alias for update_user)"""
        return await self.update_user(user)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            if not user_model:
                return False
            
            await session.delete(user_model)
            await session.commit()
            return True

    async def delete(self, user_id: str) -> bool:
        """Delete user (alias for delete_user)"""
        return await self.delete_user(user_id)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)

    async def find_all(self) -> List[User]:
        """Get all users"""
        async for session in get_db():
            result = await session.execute(select(UserModel))
            users = result.scalars().all()
            return [self._user_model_to_entity(user) for user in users]

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            return result.scalar_one_or_none() is not None

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.username == username)
            )
            return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login time"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.id == user_id)
            )
            user_model = result.scalar_one_or_none()
            if not user_model:
                return None
            
            from datetime import datetime
            user_model.last_login = datetime.now()
            await session.commit()
            await session.refresh(user_model)
            return self._user_model_to_entity(user_model)

    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        async for session in get_db():
            result = await session.execute(
                select(func.count(UserModel.id)).where(UserModel.is_active == True)
            )
            return result.scalar()

    async def get_superusers(self) -> List[User]:
        """Get all superusers"""
        async for session in get_db():
            result = await session.execute(
                select(UserModel).where(UserModel.is_superuser == True)
            )
            users = result.scalars().all()
            return [self._user_model_to_entity(user) for user in users] 