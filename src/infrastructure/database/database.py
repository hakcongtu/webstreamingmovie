"""
Database Configuration - Infrastructure Layer
SQLAlchemy database setup and session management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Database URL - Using relative path for GitHub deployment
DATABASE_URL = "sqlite+aiosqlite:///./movielens.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    future=True
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


class Database:
    """Database management class"""
    
    def __init__(self):
        self.engine = engine
        self.session_factory = AsyncSessionLocal
    
    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        """Close database connection"""
        await self.engine.dispose()


# Global database instance
database = Database()


async def get_db():
    """Dependency to get database session"""
    async with database.session_factory() as session:
        yield session 