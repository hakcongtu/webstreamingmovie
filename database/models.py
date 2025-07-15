from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class Movie(Base):
    """Bảng chính chứa thông tin phim - Tương thích với webstreamingmovie project"""
    __tablename__ = 'movies'
    
    movieId = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    genres = Column(Text, nullable=False)  # Pipe-separated genres
    imdb_id = Column(String, nullable=False)
    tmdb_id = Column(String, nullable=False)
    ratings_count = Column(Integer, default=0)
    zero_to_one_ratings_count = Column(Integer, default=0)
    one_to_two_ratings_count = Column(Integer, default=0)
    two_to_three_ratings_count = Column(Integer, default=0)
    three_to_four_ratings_count = Column(Integer, default=0)
    four_to_five_ratings_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    tags = Column(Text, nullable=False)  # Pipe-separated tags
    earliest_rating = Column(String, nullable=False)
    latest_rating = Column(String, nullable=False)
    earliest_tag = Column(String, nullable=False)
    latest_tag = Column(String, nullable=False)
    
    # Relationships với các bảng gốc
    ratings = relationship("Rating", back_populates="movie")
    movie_tags = relationship("MovieTag", back_populates="movie")
    movie_links = relationship("MovieLink", back_populates="movie", uselist=False)

class Rating(Base):
    """Bảng đánh giá của người dùng - Dữ liệu gốc từ CSV"""
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, nullable=False, index=True)
    movieId = Column(String, ForeignKey('movies.movieId'), nullable=False, index=True)
    rating = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationship
    movie = relationship("Movie", back_populates="ratings")

class MovieTag(Base):
    """Bảng tag của người dùng - Dữ liệu gốc từ CSV"""
    __tablename__ = 'movie_tags'
    
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer, nullable=False, index=True)
    movieId = Column(String, ForeignKey('movies.movieId'), nullable=False, index=True)
    tag = Column(String(255), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    # Relationship
    movie = relationship("Movie", back_populates="movie_tags")

class MovieLink(Base):
    """Bảng liên kết với các nguồn dữ liệu khác - Dữ liệu gốc từ CSV"""
    __tablename__ = 'movie_links'
    
    id = Column(Integer, primary_key=True, index=True)
    movieId = Column(String, ForeignKey('movies.movieId'), nullable=False, unique=True, index=True)
    imdbId = Column(String(20), nullable=True)
    tmdbId = Column(String(20), nullable=True)
    
    # Relationship
    movie = relationship("Movie", back_populates="movie_links") 