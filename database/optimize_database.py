import sqlite3

def optimize_database():
    """Tối ưu hóa database với các index và constraint"""
    conn = sqlite3.connect('movielens.db')
    cursor = conn.cursor()
    
    print("=== TỐI ƯU HÓA DATABASE ===\n")
    
    # 1. Tạo index cho ratings để tối ưu hóa truy vấn theo user
    print("1. Tạo index cho ratings theo userId...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ratings_userId 
    ON ratings(userId)
    """)
    
    # 2. Tạo index cho ratings theo rating để tối ưu hóa truy vấn theo điểm số
    print("2. Tạo index cho ratings theo rating...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ratings_rating 
    ON ratings(rating)
    """)
    
    # 3. Tạo index cho movie_tags theo userId
    print("3. Tạo index cho movie_tags theo userId...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movie_tags_userId 
    ON movie_tags(userId)
    """)
    
    # 4. Tạo index cho movie_tags theo tag
    print("4. Tạo index cho movie_tags theo tag...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movie_tags_tag 
    ON movie_tags(tag)
    """)
    
    # 5. Tạo index cho movies theo title để tìm kiếm
    print("5. Tạo index cho movies theo title...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movies_title 
    ON movies(title)
    """)
    
    # 6. Tạo index cho movies theo genres
    print("6. Tạo index cho movies theo genres...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movies_genres 
    ON movies(genres)
    """)
    
    # 7. Tạo index cho movie_links theo imdbId
    print("7. Tạo index cho movie_links theo imdbId...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movie_links_imdbId 
    ON movie_links(imdbId)
    """)
    
    # 8. Tạo index cho movie_links theo tmdbId
    print("8. Tạo index cho movie_links theo tmdbId...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movie_links_tmdbId 
    ON movie_links(tmdbId)
    """)
    
    # 9. Tạo composite index cho ratings (userId, movieId)
    print("9. Tạo composite index cho ratings (userId, movieId)...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ratings_user_movie 
    ON ratings(userId, movieId)
    """)
    
    # 10. Tạo composite index cho movie_tags (userId, movieId)
    print("10. Tạo composite index cho movie_tags (userId, movieId)...")
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_movie_tags_user_movie 
    ON movie_tags(userId, movieId)
    """)
    
    # Commit changes
    conn.commit()
    
    # Hiển thị thống kê index
    print("\n=== THỐNG KÊ INDEX ===")
    cursor.execute("""
    SELECT name, sql FROM sqlite_master 
    WHERE type='index' AND name NOT LIKE 'sqlite_%'
    ORDER BY name
    """)
    
    indexes = cursor.fetchall()
    for index in indexes:
        print(f"Index: {index[0]}")
    
    # Hiển thị thống kê kích thước database
    print("\n=== THỐNG KÊ KÍCH THƯỚC ===")
    cursor.execute("PRAGMA page_count")
    page_count = cursor.fetchone()[0]
    cursor.execute("PRAGMA page_size")
    page_size = cursor.fetchone()[0]
    db_size = page_count * page_size
    print(f"Database size: {db_size / (1024*1024):.2f} MB")
    
    conn.close()
    print("\nTối ưu hóa hoàn tất!")

if __name__ == "__main__":
    optimize_database() 