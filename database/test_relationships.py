import sqlite3
import pandas as pd

def test_relationships():
    """Kiểm tra các mối quan hệ giữa các bảng"""
    conn = sqlite3.connect('movielens.db')
    
    print("=== KIỂM TRA MỐI QUAN HỆ GIỮA CÁC BẢNG ===\n")
    
    # 1. Kiểm tra số lượng phim có rating
    query1 = """
    SELECT COUNT(DISTINCT m.movieId) as movies_with_ratings
    FROM movies m
    INNER JOIN ratings r ON m.movieId = r.movieId
    """
    result1 = pd.read_sql_query(query1, conn)
    print(f"1. Số phim có rating: {result1['movies_with_ratings'].iloc[0]}")
    
    # 2. Kiểm tra số lượng phim có tag
    query2 = """
    SELECT COUNT(DISTINCT m.movieId) as movies_with_tags
    FROM movies m
    INNER JOIN movie_tags t ON m.movieId = t.movieId
    """
    result2 = pd.read_sql_query(query2, conn)
    print(f"2. Số phim có tag: {result2['movies_with_tags'].iloc[0]}")
    
    # 3. Kiểm tra số lượng phim có link
    query3 = """
    SELECT COUNT(DISTINCT m.movieId) as movies_with_links
    FROM movies m
    INNER JOIN movie_links l ON m.movieId = l.movieId
    """
    result3 = pd.read_sql_query(query3, conn)
    print(f"3. Số phim có link: {result3['movies_with_links'].iloc[0]}")
    
    # 4. Top 10 phim có nhiều rating nhất
    query4 = """
    SELECT m.title, COUNT(r.rating) as rating_count, AVG(r.rating) as avg_rating
    FROM movies m
    INNER JOIN ratings r ON m.movieId = r.movieId
    GROUP BY m.movieId, m.title
    ORDER BY rating_count DESC
    LIMIT 10
    """
    result4 = pd.read_sql_query(query4, conn)
    print("\n4. Top 10 phim có nhiều rating nhất:")
    print(result4.to_string(index=False))
    
    # 5. Top 10 phim có rating cao nhất (ít nhất 100 rating)
    query5 = """
    SELECT m.title, COUNT(r.rating) as rating_count, AVG(r.rating) as avg_rating
    FROM movies m
    INNER JOIN ratings r ON m.movieId = r.movieId
    GROUP BY m.movieId, m.title
    HAVING rating_count >= 100
    ORDER BY avg_rating DESC
    LIMIT 10
    """
    result5 = pd.read_sql_query(query5, conn)
    print("\n5. Top 10 phim có rating cao nhất (ít nhất 100 rating):")
    print(result5.to_string(index=False))
    
    # 6. Thống kê theo thể loại
    query6 = """
    SELECT 
        m.genres,
        COUNT(DISTINCT m.movieId) as movie_count,
        COUNT(r.rating) as total_ratings,
        AVG(r.rating) as avg_rating
    FROM movies m
    LEFT JOIN ratings r ON m.movieId = r.movieId
    GROUP BY m.genres
    ORDER BY movie_count DESC
    LIMIT 10
    """
    result6 = pd.read_sql_query(query6, conn)
    print("\n6. Thống kê theo thể loại (top 10):")
    print(result6.to_string(index=False))
    
    # 7. Kiểm tra dữ liệu mẫu từ tất cả các bảng
    print("\n7. Dữ liệu mẫu từ bảng movies:")
    sample_movies = pd.read_sql_query("SELECT * FROM movies LIMIT 5", conn)
    print(sample_movies.to_string(index=False))
    
    print("\n8. Dữ liệu mẫu từ bảng ratings:")
    sample_ratings = pd.read_sql_query("SELECT * FROM ratings LIMIT 5", conn)
    print(sample_ratings.to_string(index=False))
    
    print("\n9. Dữ liệu mẫu từ bảng movie_tags:")
    sample_tags = pd.read_sql_query("SELECT * FROM movie_tags LIMIT 5", conn)
    print(sample_tags.to_string(index=False))
    
    print("\n10. Dữ liệu mẫu từ bảng movie_links:")
    sample_links = pd.read_sql_query("SELECT * FROM movie_links LIMIT 5", conn)
    print(sample_links.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    test_relationships() 