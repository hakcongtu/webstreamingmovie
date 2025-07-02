"""
Check Database Schema
"""
import sqlite3
import os


def check_database_schema():
    """Check the actual database schema"""
    db_path = "./database/movielens.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"✅ Database file exists: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check movies table schema
        print(f"\n🎬 Movies table schema:")
        cursor.execute("PRAGMA table_info(movies);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check users table schema
        print(f"\n👥 Users table schema:")
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'}")
        
        # Check sample data
        print(f"\n📊 Sample data:")
        cursor.execute("SELECT COUNT(*) FROM movies;")
        movie_count = cursor.fetchone()[0]
        print(f"   - Movies: {movie_count}")
        
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"   - Users: {user_count}")
        
        # Show sample movie
        cursor.execute("SELECT * FROM movies LIMIT 1;")
        sample_movie = cursor.fetchone()
        if sample_movie:
            print(f"\n🎭 Sample movie:")
            cursor.execute("PRAGMA table_info(movies);")
            columns = cursor.fetchall()
            for i, col in enumerate(columns):
                if i < len(sample_movie):
                    print(f"   - {col[1]}: {sample_movie[i]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")


if __name__ == "__main__":
    check_database_schema() 