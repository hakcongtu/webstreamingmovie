import pandas as pd
import sqlite3
import os
from datetime import datetime
from config import DATABASE_URL, CSV_FILES, WEBSTREAMING_DATA_PATH

def convert_timestamp(timestamp):
    """Chuyển đổi timestamp thành datetime"""
    try:
        return datetime.fromtimestamp(int(timestamp))
    except (ValueError, TypeError):
        return datetime.now()

def import_movies():
    """Import và xử lý dữ liệu movies từ CSV để phù hợp với webstreamingmovie project"""
    print("Importing and processing movies...")
    movies_df = pd.read_csv(CSV_FILES['movies'])
    ratings_df = pd.read_csv(CSV_FILES['ratings'])
    tags_df = pd.read_csv(CSV_FILES['tags'])
    links_df = pd.read_csv(CSV_FILES['links'])
    
    # Tạo thư mục data nếu chưa có
    os.makedirs(WEBSTREAMING_DATA_PATH, exist_ok=True)
    
    # Kết nối database
    db_path = os.path.join(WEBSTREAMING_DATA_PATH, "movie_streaming.db")
    conn = sqlite3.connect(db_path)
    
    # Tính toán thống kê ratings cho mỗi phim
    ratings_stats = ratings_df.groupby('movieId').agg({
        'rating': ['count', 'mean'],
        'timestamp': ['min', 'max']
    }).reset_index()
    
    ratings_stats.columns = ['movieId', 'ratings_count', 'average_rating', 'earliest_rating', 'latest_rating']
    
    # Tính toán phân bố ratings
    rating_distribution_data = []
    for movie_id in ratings_df['movieId'].unique():
        movie_ratings = ratings_df[ratings_df['movieId'] == movie_id]['rating']
        zero_to_one = len(movie_ratings[(movie_ratings >= 0) & (movie_ratings < 1)])
        one_to_two = len(movie_ratings[(movie_ratings >= 1) & (movie_ratings < 2)])
        two_to_three = len(movie_ratings[(movie_ratings >= 2) & (movie_ratings < 3)])
        three_to_four = len(movie_ratings[(movie_ratings >= 3) & (movie_ratings < 4)])
        four_to_five = len(movie_ratings[(movie_ratings >= 4) & (movie_ratings <= 5)])
        
        rating_distribution_data.append({
            'movieId': movie_id,
            'zero_to_one_ratings_count': zero_to_one,
            'one_to_two_ratings_count': one_to_two,
            'two_to_three_ratings_count': two_to_three,
            'three_to_four_ratings_count': three_to_four,
            'four_to_five_ratings_count': four_to_five
        })
    
    rating_distribution = pd.DataFrame(rating_distribution_data)
    
    # Tính toán thống kê tags cho mỗi phim
    tags_stats_data = []
    for movie_id in tags_df['movieId'].unique():
        movie_tags = tags_df[tags_df['movieId'] == movie_id]
        tags_list = '|'.join(movie_tags['tag'].unique())
        earliest_tag = str(movie_tags['timestamp'].min()) if len(movie_tags) > 0 else ''
        latest_tag = str(movie_tags['timestamp'].max()) if len(movie_tags) > 0 else ''
        
        tags_stats_data.append({
            'movieId': movie_id,
            'tags': tags_list,
            'earliest_tag': earliest_tag,
            'latest_tag': latest_tag
        })
    
    tags_stats = pd.DataFrame(tags_stats_data)
    
    # Merge tất cả dữ liệu
    processed_movies = movies_df.merge(ratings_stats, on='movieId', how='left')
    processed_movies = processed_movies.merge(rating_distribution, on='movieId', how='left')
    processed_movies = processed_movies.merge(tags_stats, on='movieId', how='left')
    processed_movies = processed_movies.merge(links_df, on='movieId', how='left')
    
    # Điền giá trị mặc định cho các cột null
    processed_movies = processed_movies.fillna({
        'ratings_count': 0,
        'average_rating': 0.0,
        'zero_to_one_ratings_count': 0,
        'one_to_two_ratings_count': 0,
        'two_to_three_ratings_count': 0,
        'three_to_four_ratings_count': 0,
        'four_to_five_ratings_count': 0,
        'tags': '',
        'earliest_rating': '',
        'latest_rating': '',
        'earliest_tag': '',
        'latest_tag': '',
        'imdbId': '',
        'tmdbId': ''
    })
    
    # Đổi tên cột để phù hợp với model
    processed_movies = processed_movies.rename(columns={
        'imdbId': 'imdb_id',
        'tmdbId': 'tmdb_id'
    })
    
    # Chuyển đổi movieId thành string
    processed_movies['movieId'] = processed_movies['movieId'].astype(str)
    
    # Import vào database
    processed_movies.to_sql('movies', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Imported {len(processed_movies)} processed movies")

def import_ratings():
    """Import dữ liệu ratings từ CSV vào database gốc"""
    print("Importing ratings to original database...")
    df = pd.read_csv(CSV_FILES['ratings'])
    
    # Chuyển đổi timestamp
    df['timestamp'] = df['timestamp'].apply(convert_timestamp)
    
    # Chuyển đổi movieId thành string
    df['movieId'] = df['movieId'].astype(str)
    
    conn = sqlite3.connect('movielens.db')
    
    # Import ratings
    df.to_sql('ratings', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Imported {len(df)} ratings")

def import_tags():
    """Import dữ liệu tags từ CSV vào database gốc"""
    print("Importing tags to original database...")
    df = pd.read_csv(CSV_FILES['tags'])
    
    # Chuyển đổi timestamp
    df['timestamp'] = df['timestamp'].apply(convert_timestamp)
    
    # Chuyển đổi movieId thành string
    df['movieId'] = df['movieId'].astype(str)
    
    conn = sqlite3.connect('movielens.db')
    
    # Import tags với tên bảng mới
    df.to_sql('movie_tags', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Imported {len(df)} tags")

def import_links():
    """Import dữ liệu links từ CSV vào database gốc"""
    print("Importing links to original database...")
    df = pd.read_csv(CSV_FILES['links'])
    
    # Chuyển đổi movieId thành string
    df['movieId'] = df['movieId'].astype(str)
    
    conn = sqlite3.connect('movielens.db')
    
    # Import links với tên bảng mới
    df.to_sql('movie_links', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"Imported {len(df)} links")

def main():
    """Import tất cả dữ liệu"""
    print("Starting data import for webstreamingmovie project...")
    
    try:
        # Import dữ liệu đã xử lý vào webstreamingmovie database
        import_movies()
        
        # Import dữ liệu gốc vào database local để tham khảo
        import_ratings()
        import_tags()
        import_links()
        
        print("Data import completed successfully!")
        
        # Hiển thị thống kê database webstreamingmovie
        db_path = os.path.join(WEBSTREAMING_DATA_PATH, "movie_streaming.db")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM movies")
            count = cursor.fetchone()[0]
            print(f"Webstreamingmovie Movies: {count} records")
            
            conn.close()
        
        # Hiển thị thống kê database local
        conn = sqlite3.connect('movielens.db')
        cursor = conn.cursor()
        
        tables = ['movies', 'ratings', 'movie_tags', 'movie_links']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Local {table.capitalize()}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"Error during import: {e}")

if __name__ == "__main__":
    main() 