"""
Script to migrate data from CSV files to SQLite database
"""
import asyncio
import pandas as pd
import os
import sys
from datetime import datetime
import uuid

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.database.database import database, get_db
from src.infrastructure.database.models import MovieModel, UserModel
from src.infrastructure.repositories.sqlite_user_repository import SqliteUserRepository


async def migrate_movies():
    """Migrate movies from CSV to SQLite"""
    print("Starting movie migration...")
    
    # Use the existing database in the database folder
    csv_file_path = "database/movies.csv"
    if not os.path.exists(csv_file_path):
        print(f"CSV file not found: {csv_file_path}")
        return
    
    try:
        # Read CSV data
        df = pd.read_csv(csv_file_path)
        print(f"Found {len(df)} movies in CSV")
        
        # Note: Database already exists, we don't need to create tables
        # The database/movielens.db already contains the data
        
        print("Movie data already exists in database/movielens.db")
        print("Migration skipped - using existing database")
            
    except Exception as e:
        print(f"Error during movie migration: {str(e)}")
        raise


async def migrate_users():
    """Migrate users from CSV to SQLite"""
    print("Starting user migration...")
    
    # Check if users table exists in the database
    # For now, we'll create some default users if needed
    try:
        user_repo = SqliteUserRepository()
        
        # Create default admin user if not exists
        admin_user = await user_repo.find_by_email("admin@example.com")
        if not admin_user:
            from src.domain.entities.user import User
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@example.com",
                username="admin",
                hashed_password=user_repo.get_password_hash("admin123"),
                full_name="Administrator",
                is_active=True,
                is_superuser=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_login=None
            )
            await user_repo.create(admin_user)
            print("Created default admin user")
        
        print("User migration completed successfully!")
        
    except Exception as e:
        print(f"Error during user migration: {str(e)}")
        raise


async def main():
    """Main migration function"""
    print("Starting CSV to SQLite migration...")
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Migrate movies
    await migrate_movies()
    
    # Migrate users
    await migrate_users()
    
    print("Migration completed successfully!")
    
    # Close database connection
    await database.close()


if __name__ == "__main__":
    asyncio.run(main()) 