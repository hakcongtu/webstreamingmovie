"""
Movie Entity - Domain Model
Represents the core movie business entity with all its properties and behaviors
"""
from datetime import datetime
from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class Movie:
    """
    Movie Entity - Immutable domain object
    Contains business logic and domain rules
    """
    movieId: str
    title: str
    genres: List[str]
    imdb_id: str
    tmdb_id: str
    ratings_count: int
    zero_to_one_ratings_count: int
    one_to_two_ratings_count: int
    two_to_three_ratings_count: int
    three_to_four_ratings_count: int
    four_to_five_ratings_count: int
    average_rating: float
    tags: List[str]
    earliest_rating: str
    latest_rating: str
    earliest_tag: str
    latest_tag: str

    def __post_init__(self):
        """Domain validation rules"""
        self._validate()

    def _validate(self) -> None:
        """Validate domain rules"""
        if not self.movieId or not self.movieId.strip():
            raise ValueError("Movie ID cannot be empty")
        
        if not self.title or not self.title.strip():
            raise ValueError("Movie title cannot be empty")
        
        if not (0 <= self.average_rating <= 5):
            raise ValueError("Movie rating must be between 0 and 5")
        
        if self.ratings_count < 0:
            raise ValueError("Ratings count cannot be negative")
        
        # IMDB and TMDB IDs are optional for basic movie data
        # if not self.imdb_id:
        #     raise ValueError("IMDB ID cannot be empty")
        
        # if not self.tmdb_id:
        #     raise ValueError("TMDB ID cannot be empty")

        # Validate rating counts sum up correctly
        total_ratings = (
            self.zero_to_one_ratings_count +
            self.one_to_two_ratings_count +
            self.two_to_three_ratings_count +
            self.three_to_four_ratings_count +
            self.four_to_five_ratings_count
        )
        
        if total_ratings != self.ratings_count:
            raise ValueError("Rating breakdown does not match total ratings count")

    def is_highly_rated(self) -> bool:
        """Business logic: Check if movie is highly rated"""
        return self.average_rating >= 4.0

    def is_popular(self) -> bool:
        """Business logic: Check if movie is popular based on ratings count"""
        return self.ratings_count >= 100

    def get_primary_genre(self) -> str:
        """Business logic: Get primary genre (first genre)"""
        return self.genres[0] if self.genres else "Unknown"

    def get_positive_rating_percentage(self) -> float:
        """Business logic: Calculate percentage of positive ratings (3-5 stars)"""
        if self.ratings_count == 0:
            return 0.0
        
        positive_ratings = (
            self.three_to_four_ratings_count +
            self.four_to_five_ratings_count
        )
        return round((positive_ratings / self.ratings_count) * 100, 2)

    def get_negative_rating_percentage(self) -> float:
        """Business logic: Calculate percentage of negative ratings (1-2 stars)"""
        if self.ratings_count == 0:
            return 0.0
        
        negative_ratings = (
            self.zero_to_one_ratings_count +
            self.one_to_two_ratings_count
        )
        return round((negative_ratings / self.ratings_count) * 100, 2)

    def get_rating_distribution(self) -> dict:
        """Business logic: Get rating distribution as percentages"""
        if self.ratings_count == 0:
            return {
                "0-1": 0.0,
                "1-2": 0.0,
                "2-3": 0.0,
                "3-4": 0.0,
                "4-5": 0.0
            }
        
        return {
            "0-1": round((self.zero_to_one_ratings_count / self.ratings_count) * 100, 2),
            "1-2": round((self.one_to_two_ratings_count / self.ratings_count) * 100, 2),
            "2-3": round((self.two_to_three_ratings_count / self.ratings_count) * 100, 2),
            "3-4": round((self.three_to_four_ratings_count / self.ratings_count) * 100, 2),
            "4-5": round((self.four_to_five_ratings_count / self.ratings_count) * 100, 2)
        }

    def has_genre(self, genre: str) -> bool:
        """Business logic: Check if movie matches genre"""
        return any(g.lower() == genre.lower() for g in self.genres)

    def has_tag(self, tag: str) -> bool:
        """Business logic: Check if movie has specific tag"""
        return any(t.lower() == tag.lower() for t in self.tags)

    def matches_search_criteria(self, title_query: str = None, genre_filter: str = None, tag_filter: str = None) -> bool:
        """Business logic: Check if movie matches search criteria"""
        if title_query:
            if title_query.lower() not in self.title.lower():
                return False
        
        if genre_filter:
            if not self.has_genre(genre_filter):
                return False
        
        if tag_filter:
            if not self.has_tag(tag_filter):
                return False
        
        return True

    def is_recent(self, years_threshold: int = 5) -> bool:
        """Business logic: Check if movie is recent based on latest rating date"""
        try:
            latest_date = datetime.strptime(self.latest_rating, "%Y-%m-%d")
            current_date = datetime.now()
            years_diff = (current_date - latest_date).days / 365.25
            return years_diff <= years_threshold
        except ValueError:
            return False

    