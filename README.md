# 🎬 Movie Streaming API

A high-performance FastAPI-based movie streaming API with JWT authentication, built using Domain-Driven Design (DDD) and Clean Architecture principles.

## ✨ Features

- 🔐 **Authentication**: User registration, login, JWT token management
- 🎬 **Movies**: Browse, search, filter with detailed ratings and metadata
- 🎭 **Genres**: Genre categorization and filtering
- 🏷️ **Tags**: Rich tagging system for content discovery
- 📊 **Ratings**: Detailed rating distribution analytics
- 🔗 **Integration**: IMDB and TMDB ID support for external integrations
- 📖 **Pagination**: Efficient pagination for all endpoints
- 🔍 **Search**: Multi-criteria search with advanced filters
- ⚡ **Performance**: Optimized with caching and async operations
- 📚 **Documentation**: Interactive API documentation with Swagger UI

## 🏗️ Architecture

Built with Clean Architecture and DDD principles:

```
src/
├── domain/           # Core business logic and entities
├── application/      # Use cases and application services
├── infrastructure/   # Data access and external services
└── presentation/     # FastAPI controllers and routes
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd webstreamingmovie
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python run.py
   ```

4. **Access the API**
   - API Base URL: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d --build

# Or build and run manually
docker build -t movie-api .
docker run -p 8000:8000 movie-api
```

## 🔐 Authentication

### Demo Accounts

- **Admin User**: `admin@movieapi.com` / `admin123`
- **Demo User**: `demo@movieapi.com` / `demo123`

### Usage

1. **Register a new account**
   ```bash
   POST /api/auth/register
   {
     "email": "user@example.com",
     "password": "password123",
     "full_name": "John Doe"
   }
   ```

2. **Login to get JWT token**
   ```bash
   POST /api/auth/login
   {
     "email": "user@example.com",
     "password": "password123"
   }
   ```

3. **Use token in requests**
   ```bash
   Authorization: Bearer <your-jwt-token>
   ```

## 📚 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register new user |
| `POST` | `/login` | Login and get JWT token |
| `GET` | `/me` | Get current user info |
| `GET` | `/users` | List users (admin only) |

### Movies (`/api/movies`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all movies with pagination |
| `GET` | `/{movie_id}` | Get movie details by ID |
| `GET` | `/search` | Search movies with criteria |
| `GET` | `/popular` | Get popular movies |
| `GET` | `/highly-rated` | Get highly rated movies |
| `GET` | `/genre/{genre}` | Get movies by genre |
| `GET` | `/tag/{tag}` | Get movies by tag |
| `GET` | `/imdb/{imdb_id}` | Get movie by IMDB ID |
| `GET` | `/tmdb/{tmdb_id}` | Get movie by TMDB ID |
| `POST` | `/{movie_id}/view` | Increment movie views |

### Genres (`/api/genres`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | List all available genres |

## 🔍 Search Features

### Search Parameters

- **title**: Search by movie title
- **genre**: Filter by genre
- **year**: Filter by release year
- **min_rating**: Minimum rating filter
- **max_rating**: Maximum rating filter
- **page**: Page number for pagination
- **limit**: Items per page (max 100)

### Example Search

```bash
GET /api/movies/search?title=action&genre=Action&year=2020&min_rating=4.0&page=1&limit=20
```

## 📊 Data Structure

### Movie Entity

```json
{
  "movieId": "1",
  "title": "Toy Story (1995)",
  "genres": ["Animation", "Children", "Comedy"],
  "imdb_id": "tt0114709",
  "tmdb_id": "862",
  "ratings_count": 215,
  "average_rating": 4.2,
  "tags": ["funny", "animation", "pixar"],
  "earliest_rating": "1995-01-01",
  "latest_rating": "2023-12-31"
}
```

### Rating Distribution

Each movie includes detailed rating breakdowns:
- `zero_to_one_ratings_count`: 0-1 star ratings
- `one_to_two_ratings_count`: 1-2 star ratings
- `two_to_three_ratings_count`: 2-3 star ratings
- `three_to_four_ratings_count`: 3-4 star ratings
- `four_to_five_ratings_count`: 4-5 star ratings

## 🛠️ Development

### Project Structure

```
webstreamingmovie/
├── src/
│   ├── domain/              # Domain layer
│   │   ├── entities/        # Business entities
│   │   ├── repositories/    # Repository interfaces
│   │   └── value_objects/   # Value objects
│   ├── application/         # Application layer
│   │   ├── use_cases/       # Business use cases
│   │   ├── services/        # Application services
│   │   ├── dtos/           # Data transfer objects
│   │   └── mappers/        # Object mappers
│   ├── infrastructure/      # Infrastructure layer
│   │   ├── repositories/    # Repository implementations
│   │   ├── cache/          # Caching layer
│   │   ├── config/         # Configuration
│   │   └── database/       # Database models
│   └── presentation/        # Presentation layer
│       ├── routers/        # FastAPI routers
│       ├── middleware/     # Custom middleware
│       └── main.py         # FastAPI app
├── data/                   # Data files
│   ├── movies.csv         # Movie data
│   └── users.csv          # User data
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

### Key Technologies

- **FastAPI**: Modern, fast web framework
- **JWT**: JSON Web Tokens for authentication
- **bcrypt**: Password hashing
- **pandas**: Data processing and CSV handling
- **SQLAlchemy**: Database ORM (for future use)
- **Docker**: Containerization
- **Pydantic**: Data validation and serialization

### Code Quality

- **Type Hints**: Full type annotation support
- **Async/Await**: Non-blocking operations
- **Error Handling**: Comprehensive error management
- **Logging**: Structured logging throughout
- **Testing**: Unit and integration tests

## 🚀 Deployment

### Render Deployment

1. **Connect to Render**
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Create a new Web Service

2. **Configure the service**
   ```
   Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
   Start Command: python start_render.py
   ```

3. **Environment Variables**
   ```
   PYTHONPATH: /opt/render/project/src/src
   CSV_FILE_PATH: /opt/render/project/src/data/movies.csv
   ENVIRONMENT: production
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PYTHONPATH` | Python path for imports | `/opt/render/project/src/src` |
| `CSV_FILE_PATH` | Path to movies CSV file | `data/movies.csv` |
| `ENVIRONMENT` | Environment (dev/prod) | `development` |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry time | `30` |

## 📈 Performance

### Optimizations

- **Caching**: In-memory caching for frequently accessed data
- **Async Operations**: Non-blocking I/O operations
- **Pagination**: Efficient data pagination
- **Search Indexing**: Optimized search with indexing
- **Response Compression**: Gzip compression for responses

### Benchmarks

- **Response Time**: < 500ms for most endpoints
- **Search Performance**: Sub-second search results
- **Concurrent Users**: Supports 100+ concurrent requests
- **Memory Usage**: Optimized for low memory footprint

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_movies.py
```

### Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test fixtures
└── conftest.py        # Test configuration
```

## 🔧 Configuration

### Development Settings

```python
# Development configuration
ENVIRONMENT = "development"
DEBUG = True
LOG_LEVEL = "DEBUG"
CACHE_TTL = 300  # 5 minutes
```

### Production Settings

```python
# Production configuration
ENVIRONMENT = "production"
DEBUG = False
LOG_LEVEL = "INFO"
CACHE_TTL = 1800  # 30 minutes
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run tests** to ensure everything works
6. **Commit your changes**
   ```bash
   git commit -m "Add amazing feature"
   ```
7. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
8. **Create a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for all classes and methods
- Include tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

- **Documentation**: Check the API docs at `/docs`
- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions for questions

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` is set correctly
2. **File Not Found**: Check if CSV files exist in `data/` directory
3. **Authentication Errors**: Verify JWT token is valid and not expired
4. **Performance Issues**: Check cache configuration and data file size

## 📊 API Statistics

- **Total Movies**: 10,000+ movies
- **Genres**: 20+ unique genres
- **Tags**: 1,000+ unique tags
- **Ratings**: Detailed rating distributions
- **API Endpoints**: 15+ endpoints
- **Response Time**: < 500ms average

## 🔮 Roadmap

- [ ] Database integration (PostgreSQL)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] Movie recommendations engine
- [ ] User watchlists
- [ ] Social features (reviews, comments)
- [ ] Mobile app support
- [ ] Internationalization (i18n)

---

**Built with ❤️ using FastAPI and Clean Architecture** 