"""
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
