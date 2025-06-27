"""
CSV User Repository Implementation - Infrastructure Layer
Implements the IUserRepository interface using CSV file as data source
"""
import csv
import os
from typing import List, Optional
from datetime import datetime
import pandas as pd

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository


class CsvUserRepository(IUserRepository):
    """
    CSV User Repository - Infrastructure Layer
    Implements user data access using CSV file
    """

    def __init__(self, csv_file_path: str = "data/users.csv"):
        self.csv_file_path = csv_file_path
        self._users_cache: Optional[List[User]] = None

    async def _load_users(self) -> List[User]:
        """(Private) Load users from CSV file with caching. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        if self._users_cache is not None:
            return self._users_cache

        if not os.path.exists(self.csv_file_path):
            # Create empty CSV file if it doesn't exist
            self._create_empty_csv()
            return []

        users = []
        try:
            df = pd.read_csv(self.csv_file_path)
            
            for _, row in df.iterrows():
                # Handle None/NaN values
                last_login = None
                if pd.notna(row['last_login']) and row['last_login']:
                    try:
                        last_login = datetime.fromisoformat(str(row['last_login']))
                    except ValueError:
                        last_login = None
                
                user = User(
                    id=str(row['id']),
                    email=str(row['email']),
                    username=str(row['username']),
                    hashed_password=str(row['hashed_password']),
                    full_name=str(row['full_name']),
                    is_active=bool(row['is_active']),
                    is_superuser=bool(row['is_superuser']),
                    created_at=datetime.fromisoformat(str(row['created_at'])),
                    updated_at=datetime.fromisoformat(str(row['updated_at'])),
                    last_login=last_login
                )
                users.append(user)
                
        except Exception as e:
            raise ValueError(f"Error loading users from CSV: {str(e)}")

        self._users_cache = users
        return users

    def _create_empty_csv(self):
        """(Private) Create empty CSV file with headers. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
        with open(self.csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'id', 'email', 'username', 'hashed_password', 'full_name',
                'is_active', 'is_superuser', 'created_at', 'updated_at', 'last_login'
            ])

    async def _save_users(self, users: List[User]) -> None:
        """(Private) Save users to CSV file. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        try:
            with open(self.csv_file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                # Write header
                writer.writerow([
                    'id', 'email', 'username', 'hashed_password', 'full_name',
                    'is_active', 'is_superuser', 'created_at', 'updated_at', 'last_login'
                ])
                
                # Write user data
                for user in users:
                    last_login_str = user.last_login.isoformat() if user.last_login else ""
                    writer.writerow([
                        user.id,
                        user.email,
                        user.username,
                        user.hashed_password,
                        user.full_name,
                        user.is_active,
                        user.is_superuser,
                        user.created_at.isoformat(),
                        user.updated_at.isoformat(),
                        last_login_str
                    ])
            
            # Update cache
            self._users_cache = users
            
        except Exception as e:
            raise ValueError(f"Error saving users to CSV: {str(e)}")

    async def create_user(self, user: User) -> User:
        """Create a new user"""
        users = await self._load_users()
        
        # Check if user ID already exists
        if any(u.id == user.id for u in users):
            raise ValueError(f"User with ID {user.id} already exists")
        
        # Check if email already exists
        if any(u.email.lower() == user.email.lower() for u in users):
            raise ValueError(f"User with email {user.email} already exists")
        
        # Check if username already exists
        if any(u.username.lower() == user.username.lower() for u in users):
            raise ValueError(f"User with username {user.username} already exists")
        
        # Add new user
        users.append(user)
        await self._save_users(users)
        
        return user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        users = await self._load_users()
        for user in users:
            if user.id == user_id:
                return user
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        users = await self._load_users()
        for user in users:
            if user.email.lower() == email.lower():
                return user
        return None

    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        users = await self._load_users()
        for user in users:
            if user.username.lower() == username.lower():
                return user
        return None

    async def update_user(self, updated_user: User) -> User:
        """Update user information"""
        users = await self._load_users()
        
        for i, user in enumerate(users):
            if user.id == updated_user.id:
                users[i] = updated_user
                await self._save_users(users)
                return updated_user
        
        raise ValueError(f"User with ID {updated_user.id} not found")

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        users = await self._load_users()
        
        for i, user in enumerate(users):
            if user.id == user_id:
                users.pop(i)
                await self._save_users(users)
                return True
        
        return False

    async def find_all(self) -> List[User]:
        """Get all users"""
        return await self._load_users()

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        users = await self._load_users()
        return any(user.email.lower() == email.lower() for user in users)

    async def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        users = await self._load_users()
        return any(user.username.lower() == username.lower() for user in users)

    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login time"""
        users = await self._load_users()
        
        for i, user in enumerate(users):
            if user.id == user_id:
                updated_user = user.update_last_login()
                users[i] = updated_user
                await self._save_users(users)
                return updated_user
        
        return None

    async def get_active_users_count(self) -> int:
        """Get count of active users"""
        users = await self._load_users()
        return sum(1 for user in users if user.is_active)

    async def get_superusers(self) -> List[User]:
        """Get all superusers"""
        users = await self._load_users()
        return [user for user in users if user.is_superuser]

    def clear_cache(self):
        """Clear the users cache (dùng khi cần reload dữ liệu từ file)"""
        self._users_cache = None

    async def _load_users(self) -> List[User]:
        """(Private) Load users from CSV file with caching. Chỉ dùng trong nội bộ class, không gọi từ ngoài class."""
        if self._users_cache is not None:
            return self._users_cache

        if not os.path.exists(self.csv_file_path):
            # Create empty CSV file if it doesn't exist
            self._create_empty_csv()
            return []

        users = []
        try:
            df = pd.read_csv(self.csv_file_path)
            
            for _, row in df.iterrows():
                # Handle None/NaN values
                last_login = None
                if pd.notna(row['last_login']) and row['last_login']:
                    try:
                        last_login = datetime.fromisoformat(str(row['last_login']))
                    except ValueError:
                        last_login = None
                
                user = User(
                    id=str(row['id']),
                    email=str(row['email']),
                    username=str(row['username']),
                    hashed_password=str(row['hashed_password']),
                    full_name=str(row['full_name']),
                    is_active=bool(row['is_active']),
                    is_superuser=bool(row['is_superuser']),
                    created_at=datetime.fromisoformat(str(row['created_at'])),
                    updated_at=datetime.fromisoformat(str(row['updated_at'])),
                    last_login=last_login
                )
                users.append(user)
                
        except Exception as e:
            raise ValueError(f"Error loading users from CSV: {str(e)}")

        self._users_cache = users
        return users 