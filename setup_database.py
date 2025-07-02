"""
Setup Database - Initialize and configure database for the application
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.database.database import database
from src.infrastructure.database.models import Base


async def setup_database():
    """Setup database tables and initial data"""
    print("Setting up database...")
    
    # Ensure database directory exists
    db_dir = Path("./database")
    db_dir.mkdir(exist_ok=True)
    
    # Check if database file exists
    db_file = db_dir / "movielens.db"
    if db_file.exists():
        print(f"Database file exists: {db_file}")
        print("Using existing database with MovieLens data")
    else:
        print(f"Database file not found: {db_file}")
        print("Please ensure the database file is in the database/ directory")
        return
    
    try:
        # Create tables if they don't exist
        await database.create_tables()
        print("Database tables created/verified successfully!")
        
        # Run migration script
        print("Running migration script...")
        from migrate_csv_to_sqlite import main as run_migration
        await run_migration()
        
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
        raise
    finally:
        await database.close()


if __name__ == "__main__":
    asyncio.run(setup_database()) 