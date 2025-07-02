# Database Setup Guide

## Overview
This project uses SQLite database with Alembic for migrations. The database file is located at `./database/movielens.db`.

## Database Structure
- **Location**: `./database/movielens.db`
- **Type**: SQLite with async support (aiosqlite)
- **Migration Tool**: Alembic

## Setup Instructions

### 1. Prerequisites
Make sure you have the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Configuration
The database is configured to use relative paths for GitHub deployment:
- Database URL: `sqlite+aiosqlite:///./database/movielens.db`
- Alembic config: `sqlite:///./database/movielens.db`

### 3. Check Database
Run the database check script:
```bash
python check_database.py
```

This will verify:
- Database file exists
- Connection works
- Tables are accessible
- Sample data is available

### 4. Setup Database (if needed)
If you need to set up the database from scratch:
```bash
python setup_database.py
```

### 5. Run Migrations
If you need to run Alembic migrations:
```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## Repository Configuration

### Movie Repository
The application uses `SqliteMovieRepository` which:
- Connects to the SQLite database
- Implements all movie-related operations
- Uses async/await for database operations

### User Repository
The application uses `SqliteUserRepository` which:
- Manages user authentication
- Handles password hashing
- Provides user CRUD operations

## File Structure
```
webstreamingmovie/
├── database/
│   ├── movielens.db          # Main database file
│   ├── movies.csv            # Source data
│   └── ...
├── src/
│   └── infrastructure/
│       ├── database/
│       │   ├── database.py   # Database configuration
│       │   └── models.py     # SQLAlchemy models
│       └── repositories/
│           ├── sqlite_movie_repository.py
│           └── sqlite_user_repository.py
├── alembic/                  # Migration files
├── alembic.ini              # Alembic configuration
└── ...
```

## GitHub Deployment
The database is configured to work with GitHub:
- Uses relative paths
- Database file is included in repository
- No absolute paths required

## Troubleshooting

### Database not found
If you get "Database file not found" error:
1. Ensure `./database/movielens.db` exists
2. Check file permissions
3. Run `python check_database.py` to verify

### Migration errors
If Alembic migrations fail:
1. Check `alembic.ini` configuration
2. Ensure database file is writable
3. Try running `alembic upgrade head`

### Connection errors
If database connection fails:
1. Check if aiosqlite is installed
2. Verify database file path
3. Check for file corruption

## Default Users
The system creates a default admin user:
- Email: `admin@example.com`
- Username: `admin`
- Password: `admin123`

## Notes
- The database file is included in the repository for easy deployment
- All paths are relative for GitHub compatibility
- Async operations are used throughout for better performance 