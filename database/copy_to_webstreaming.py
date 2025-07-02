import shutil
import os
from config import WEBSTREAMING_DATA_PATH

def copy_database_to_webstreaming():
    """Copy database đã xử lý vào project webstreamingmovie"""
    print("=== COPY DATABASE TO WEBSTREAMING PROJECT ===\n")
    
    # Đường dẫn database nguồn và đích
    source_db = os.path.join(WEBSTREAMING_DATA_PATH, "movie_streaming.db")
    target_db = os.path.join(WEBSTREAMING_DATA_PATH, "movie_streaming.db")
    
    if os.path.exists(source_db):
        try:
            # Copy database
            shutil.copy2(source_db, target_db)
            print(f"✅ Database copied successfully to: {target_db}")
            
            # Kiểm tra kích thước file
            size_mb = os.path.getsize(target_db) / (1024 * 1024)
            print(f"📊 Database size: {size_mb:.2f} MB")
            
            # Kiểm tra số lượng records
            import sqlite3
            conn = sqlite3.connect(target_db)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM movies")
            movie_count = cursor.fetchone()[0]
            print(f"🎬 Movies in database: {movie_count}")
            
            # Kiểm tra một số records mẫu
            cursor.execute("SELECT movieId, title, average_rating, ratings_count FROM movies LIMIT 5")
            sample_movies = cursor.fetchall()
            print("\n📋 Sample movies:")
            for movie in sample_movies:
                print(f"  - {movie[1]} (ID: {movie[0]}, Rating: {movie[2]:.2f}, Count: {movie[3]})")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error copying database: {e}")
    else:
        print(f"❌ Source database not found: {source_db}")
        print("Please run import_data.py first to create the database.")

def verify_webstreaming_compatibility():
    """Kiểm tra tính tương thích với webstreamingmovie project"""
    print("\n=== VERIFYING WEBSTREAMING COMPATIBILITY ===\n")
    
    db_path = os.path.join(WEBSTREAMING_DATA_PATH, "movie_streaming.db")
    
    if os.path.exists(db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kiểm tra cấu trúc bảng movies
        cursor.execute("PRAGMA table_info(movies)")
        columns = cursor.fetchall()
        
        required_columns = [
            'movieId', 'title', 'genres', 'imdb_id', 'tmdb_id',
            'ratings_count', 'average_rating', 'tags',
            'zero_to_one_ratings_count', 'one_to_two_ratings_count',
            'two_to_three_ratings_count', 'three_to_four_ratings_count',
            'four_to_five_ratings_count'
        ]
        
        existing_columns = [col[1] for col in columns]
        
        print("📋 Checking required columns:")
        for col in required_columns:
            if col in existing_columns:
                print(f"  ✅ {col}")
            else:
                print(f"  ❌ {col} - MISSING")
        
        # Kiểm tra dữ liệu mẫu
        cursor.execute("SELECT movieId, title, genres, average_rating FROM movies LIMIT 1")
        sample = cursor.fetchone()
        
        if sample:
            print(f"\n📊 Sample data verification:")
            print(f"  Movie ID: {sample[0]} (type: {type(sample[0]).__name__})")
            print(f"  Title: {sample[1]}")
            print(f"  Genres: {sample[2]}")
            print(f"  Average Rating: {sample[3]}")
            
            # Kiểm tra kiểu dữ liệu
            if isinstance(sample[0], str):
                print("  ✅ Movie ID is string (compatible with webstreaming)")
            else:
                print("  ⚠️ Movie ID is not string (may cause issues)")
        
        conn.close()
    else:
        print("❌ Database not found. Please run import_data.py first.")

def main():
    """Main function"""
    print("🚀 Starting webstreamingmovie integration...\n")
    
    # Tạo thư mục data nếu chưa có
    os.makedirs(WEBSTREAMING_DATA_PATH, exist_ok=True)
    print(f"📁 Data directory: {WEBSTREAMING_DATA_PATH}")
    
    # Copy database
    copy_database_to_webstreaming()
    
    # Verify compatibility
    verify_webstreaming_compatibility()
    
    print("\n🎉 Integration completed!")
    print("\n📝 Next steps:")
    print("1. Navigate to webstreamingmovie project directory")
    print("2. Run the webstreamingmovie application")
    print("3. The database should now be compatible with the project")

if __name__ == "__main__":
    main() 