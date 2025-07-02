#!/usr/bin/env python3
"""
Update Movies Table Schema and Import Complete Data
This script updates the movies table to match the movies.csv structure
and imports all the data from the CSV file.
"""
import sqlite3
import pandas as pd
import os
from pathlib import Path

def update_movies_schema():
    """Update movies table schema to match movies.csv"""
    db_path = Path("./database/movielens.db")
    csv_path = Path("./data/movies.csv")
    
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    if not csv_path.exists():
        print("❌ movies.csv file not found!")
        return False
    
    print("🔄 Updating movies table schema...")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Read CSV data
        print("📖 Reading movies.csv...")
        df = pd.read_csv(csv_path)
        print(f"📊 Found {len(df)} movies in CSV")
        
        # Check current schema
        cursor.execute("PRAGMA table_info(movies)")
        current_columns = {row[1] for row in cursor.fetchall()}
        print(f"📋 Current columns: {current_columns}")
        
        # Define all required columns based on CSV
        required_columns = {
            'movieId': 'INTEGER PRIMARY KEY',
            'title': 'TEXT',
            'genres': 'TEXT',
            'imdb_id': 'TEXT',
            'tmdb_id': 'TEXT',
            'ratings_count': 'INTEGER',
            'zero_to_one_ratings_count': 'INTEGER',
            'one_to_two_ratings_count': 'INTEGER',
            'two_to_three_ratings_count': 'INTEGER',
            'three_to_four_ratings_count': 'INTEGER',
            'four_to_five_ratings_count': 'INTEGER',
            'average_rating': 'REAL',
            'tags': 'TEXT',
            'earliest_rating': 'TEXT',
            'latest_rating': 'TEXT',
            'earliest_tag': 'TEXT',
            'latest_tag': 'TEXT'
        }
        
        # Add missing columns
        missing_columns = set(required_columns.keys()) - current_columns
        if missing_columns:
            print(f"🔧 Adding missing columns: {missing_columns}")
            for col in missing_columns:
                col_type = required_columns[col]
                if col == 'movieId':
                    # Skip movieId as it's already the primary key
                    continue
                try:
                    cursor.execute(f"ALTER TABLE movies ADD COLUMN {col} {col_type}")
                    print(f"   ✅ Added column: {col}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        print(f"   ⚠️  Column {col} already exists")
                    else:
                        print(f"   ❌ Error adding column {col}: {e}")
        else:
            print("✅ All required columns already exist")
        
        # Clear existing data
        print("🗑️  Clearing existing movies data...")
        cursor.execute("DELETE FROM movies")
        
        # Insert new data from CSV
        print("📥 Inserting data from CSV...")
        for index, row in df.iterrows():
            try:
                cursor.execute("""
                    INSERT INTO movies (
                        movieId, title, genres, imdb_id, tmdb_id,
                        ratings_count, zero_to_one_ratings_count, one_to_two_ratings_count,
                        two_to_three_ratings_count, three_to_four_ratings_count, four_to_five_ratings_count,
                        average_rating, tags, earliest_rating, latest_rating, earliest_tag, latest_tag
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['movieId'], row['title'], row['genres'], row['imdb_id'], row['tmdb_id'],
                    row['ratings_count'], row['zero_to_one_ratings_count'], row['one_to_two_ratings_count'],
                    row['two_to_three_ratings_count'], row['three_to_four_ratings_count'], row['four_to_five_ratings_count'],
                    row['average_rating'], row['tags'], row['earliest_rating'], row['latest_rating'],
                    row['earliest_tag'], row['latest_tag']
                ))
            except Exception as e:
                print(f"❌ Error inserting row {index}: {e}")
                print(f"   Data: {row.to_dict()}")
        
        # Commit changes
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT COUNT(*) FROM movies")
        count = cursor.fetchone()[0]
        print(f"✅ Successfully imported {count} movies")
        
        # Show sample data
        cursor.execute("SELECT * FROM movies LIMIT 3")
        sample_rows = cursor.fetchall()
        print("\n📋 Sample data:")
        for row in sample_rows:
            print(f"   - Movie ID: {row[0]}, Title: {row[1]}, Rating: {row[12]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

def update_sqlalchemy_models():
    """Update SQLAlchemy models to match the new schema"""
    print("\n🔄 Updating SQLAlchemy models...")
    
    model_content = '''"""
Database Models - Infrastructure Layer
SQLAlchemy ORM models for database tables
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Float, Text
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base


class UserModel(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)


class MovieModel(Base):
    """Movie database model"""
    __tablename__ = "movies"
    
    movieId = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    genres = Column(Text, nullable=True)  # Pipe-separated genres
    imdb_id = Column(String, nullable=True)
    tmdb_id = Column(String, nullable=True)
    ratings_count = Column(Integer, nullable=True)
    zero_to_one_ratings_count = Column(Integer, nullable=True)
    one_to_two_ratings_count = Column(Integer, nullable=True)
    two_to_three_ratings_count = Column(Integer, nullable=True)
    three_to_four_ratings_count = Column(Integer, nullable=True)
    four_to_five_ratings_count = Column(Integer, nullable=True)
    average_rating = Column(Float, nullable=True)
    tags = Column(Text, nullable=True)  # Pipe-separated tags
    earliest_rating = Column(String, nullable=True)
    latest_rating = Column(String, nullable=True)
    earliest_tag = Column(String, nullable=True)
    latest_tag = Column(String, nullable=True)
'''
    
    try:
        with open("src/infrastructure/database/models.py", "w", encoding="utf-8") as f:
            f.write(model_content)
        print("✅ Updated SQLAlchemy models")
        return True
    except Exception as e:
        print(f"❌ Error updating models: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting movies schema update...")
    print("=" * 50)
    
    # Update database schema
    if update_movies_schema():
        print("\n✅ Database schema updated successfully!")
    else:
        print("\n❌ Failed to update database schema!")
        return
    
    # Update SQLAlchemy models
    if update_sqlalchemy_models():
        print("✅ SQLAlchemy models updated successfully!")
    else:
        print("❌ Failed to update SQLAlchemy models!")
        return
    
    print("\n🎉 All updates completed successfully!")
    print("📝 Next steps:")
    print("   1. Restart the FastAPI server")
    print("   2. Test the movie endpoints")
    print("   3. Verify that all movie data is now available")

if __name__ == "__main__":
    main() 