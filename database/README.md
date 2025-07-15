# MovieLens Database với Alembic - Tích hợp WebStreamingMovie

Dự án này sử dụng Alembic để tạo và quản lý cơ sở dữ liệu quan hệ từ 4 file CSV của MovieLens dataset, được tối ưu hóa để tích hợp với project WebStreamingMovie.

## Cấu trúc dự án

```
archive/
├── alembic/                 # Thư mục chứa migrations
├── movies.csv              # Dữ liệu phim (9,742 phim)
├── ratings.csv             # Dữ liệu đánh giá (100,836 đánh giá)
├── tags.csv                # Dữ liệu tag (3,683 tag)
├── links.csv               # Dữ liệu liên kết (9,742 liên kết)
├── models.py               # SQLAlchemy models (tương thích WebStreamingMovie)
├── config.py               # Cấu hình database (tương thích WebStreamingMovie)
├── import_data.py          # Script import và xử lý dữ liệu
├── test_relationships.py   # Script kiểm tra mối quan hệ
├── optimize_database.py    # Script tối ưu hóa database
├── copy_to_webstreaming.py # Script tích hợp với WebStreamingMovie
├── requirements.txt        # Dependencies
└── README.md              # Hướng dẫn này
```

## Cấu trúc Database

### Bảng Movies (Bảng chính) - Tương thích WebStreamingMovie
- `movieId` (STRING, PRIMARY KEY): ID phim
- `title` (STRING): Tên phim
- `genres` (TEXT): Thể loại phim (pipe-separated)
- `imdb_id` (STRING): ID IMDB
- `tmdb_id` (STRING): ID TMDB
- `ratings_count` (INTEGER): Số lượng đánh giá
- `average_rating` (FLOAT): Điểm đánh giá trung bình
- `zero_to_one_ratings_count` (INTEGER): Số đánh giá 0-1 sao
- `one_to_two_ratings_count` (INTEGER): Số đánh giá 1-2 sao
- `two_to_three_ratings_count` (INTEGER): Số đánh giá 2-3 sao
- `three_to_four_ratings_count` (INTEGER): Số đánh giá 3-4 sao
- `four_to_five_ratings_count` (INTEGER): Số đánh giá 4-5 sao
- `tags` (TEXT): Tags (pipe-separated)
- `earliest_rating` (STRING): Đánh giá sớm nhất
- `latest_rating` (STRING): Đánh giá muộn nhất
- `earliest_tag` (STRING): Tag sớm nhất
- `latest_tag` (STRING): Tag muộn nhất

### Bảng Ratings
- `id` (INTEGER, PRIMARY KEY): ID tự động
- `userId` (INTEGER): ID người dùng
- `movieId` (INTEGER, FOREIGN KEY): ID phim
- `rating` (REAL): Điểm đánh giá (0.5 - 5.0)
- `timestamp` (DATETIME): Thời gian đánh giá

### Bảng MovieTags (Dữ liệu gốc)
- `id` (INTEGER, PRIMARY KEY): ID tự động
- `userId` (INTEGER): ID người dùng
- `movieId` (STRING, FOREIGN KEY): ID phim
- `tag` (TEXT): Tag do người dùng tạo
- `timestamp` (DATETIME): Thời gian tạo tag

### Bảng MovieLinks (Dữ liệu gốc)
- `id` (INTEGER, PRIMARY KEY): ID tự động
- `movieId` (STRING, FOREIGN KEY, UNIQUE): ID phim
- `imdbId` (TEXT): ID IMDB
- `tmdbId` (TEXT): ID TMDB

## Mối quan hệ

- **Movies** ↔ **Ratings**: One-to-Many (1 phim có nhiều đánh giá)
- **Movies** ↔ **MovieTags**: One-to-Many (1 phim có nhiều tag)
- **Movies** ↔ **MovieLinks**: One-to-One (1 phim có 1 liên kết)

## Tích hợp với WebStreamingMovie

Dự án này được thiết kế để tương thích hoàn toàn với project WebStreamingMovie:

- **Cấu trúc database**: Tương thích với MovieModel trong WebStreamingMovie
- **Kiểu dữ liệu**: movieId được chuyển đổi thành string
- **Thống kê**: Tự động tính toán các thống kê cần thiết
- **Đường dẫn**: Database được tạo trong thư mục data của WebStreamingMovie

## Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Khởi tạo Alembic (đã thực hiện)
```bash
python -m alembic init alembic
```

### 3. Tạo migration và chạy
```bash
python -m alembic revision --autogenerate -m "Create initial tables"
python -m alembic upgrade head
```

### 4. Import dữ liệu
```bash
python import_data.py
```

### 5. Tối ưu hóa database
```bash
python optimize_database.py
```

### 6. Kiểm tra mối quan hệ
```bash
python test_relationships.py
```

### 7. Tích hợp với WebStreamingMovie
```bash
python copy_to_webstreaming.py
```

## Thống kê dữ liệu

- **Movies**: 9,742 phim
- **Ratings**: 100,836 đánh giá
- **Tags**: 3,683 tag
- **Links**: 9,742 liên kết
- **Users**: 610 người dùng
- **Database size**: ~8.82 MB

## Các truy vấn mẫu

### 1. Tìm phim có nhiều rating nhất
```sql
SELECT m.title, COUNT(r.rating) as rating_count, AVG(r.rating) as avg_rating
FROM movies m
INNER JOIN ratings r ON m.movieId = r.movieId
GROUP BY m.movieId, m.title
ORDER BY rating_count DESC
LIMIT 10
```

### 2. Tìm phim có rating cao nhất
```sql
SELECT m.title, COUNT(r.rating) as rating_count, AVG(r.rating) as avg_rating
FROM movies m
INNER JOIN ratings r ON m.movieId = r.movieId
GROUP BY m.movieId, m.title
HAVING rating_count >= 100
ORDER BY avg_rating DESC
LIMIT 10
```

### 3. Thống kê theo thể loại
```sql
SELECT 
    m.genres,
    COUNT(DISTINCT m.movieId) as movie_count,
    COUNT(r.rating) as total_ratings,
    AVG(r.rating) as avg_rating
FROM movies m
LEFT JOIN ratings r ON m.movieId = r.movieId
GROUP BY m.genres
ORDER BY movie_count DESC
```

## Lợi ích của việc sử dụng Alembic

1. **Quản lý schema**: Theo dõi thay đổi cấu trúc database
2. **Version control**: Mỗi thay đổi được ghi lại với version
3. **Rollback**: Có thể quay lại phiên bản trước
4. **Collaboration**: Nhiều developer có thể làm việc cùng lúc
5. **Production safe**: An toàn khi deploy lên production

## Các index đã tạo

- `idx_ratings_userId`: Tối ưu truy vấn theo user
- `idx_ratings_rating`: Tối ưu truy vấn theo điểm số
- `idx_ratings_user_movie`: Composite index cho ratings
- `idx_tags_userId`: Tối ưu truy vấn tag theo user
- `idx_tags_tag`: Tối ưu tìm kiếm tag
- `idx_tags_user_movie`: Composite index cho tags
- `idx_movies_title`: Tối ưu tìm kiếm theo tên phim
- `idx_movies_genres`: Tối ưu tìm kiếm theo thể loại
- `idx_links_imdbId`: Tối ưu tìm kiếm theo IMDB ID
- `idx_links_tmdbId`: Tối ưu tìm kiếm theo TMDB ID

## Lưu ý

- Database sử dụng SQLite để dễ dàng chạy và test
- Có thể chuyển sang PostgreSQL/MySQL cho production
- Tất cả foreign key constraints đã được thiết lập
- Timestamp được chuyển đổi từ Unix timestamp sang datetime 