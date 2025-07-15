"""
Check Database Connection and Tables
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.database.database import database, get_db
from src.infrastructure.database.models import MovieModel, UserModel
from sqlalchemy import select, func


async def check_database():
    """Check database connection and tables"""
    print("Checking database connection...")
    
    # Check if database file exists
    db_file = Path("./database/movielens.db")
    if not db_file.exists():
        print(f"❌ Database file not found: {db_file}")
        return
    
    print(f"✅ Database file exists: {db_file}")
    
    try:
        # Test connection
        async for session in get_db():
            # Check movies table
            result = await session.execute(select(func.count(MovieModel.movieId)))
            movie_count = result.scalar()
            print(f"✅ Movies table: {movie_count} records")
            
            # Check users table
            result = await session.execute(select(func.count(UserModel.id)))
            user_count = result.scalar()
            print(f"✅ Users table: {user_count} records")
            
            # Show sample data
            if movie_count > 0:
                result = await session.execute(select(MovieModel).limit(3))
                movies = result.scalars().all()
                print("\n📽️ Sample movies:")
                for movie in movies:
                    print(f"   - {movie.title} (ID: {movie.movieId})")
            
            if user_count > 0:
                result = await session.execute(select(UserModel).limit(3))
                users = result.scalars().all()
                print("\n👥 Sample users:")
                for user in users:
                    print(f"   - {user.email} ({user.username})")
            
            break
        
        print("\n✅ Database connection successful!")
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        raise
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(check_database()) 