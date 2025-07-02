"""
SearchCriteria Value Object - Domain Layer
Represents search criteria for movies with validation
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class SearchCriteria:
    """
    SearchCriteria Value Object
    Represents search criteria for movies with validation
    """
    title: Optional[str] = None
    genre: Optional[str] = None
    year: Optional[int] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    country: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None

    def __post_init__(self):
        """Validation rules for search criteria"""
        self._validate()

    def _validate(self) -> None:
        """Validate search criteria"""
        if self.title is not None and not self.title.strip():
            raise ValueError("Title search term cannot be empty")

        current_year = datetime.now().year
        if self.year is not None and (self.year < 1888 or self.year > current_year + 5):
            raise ValueError(f"Invalid year for search: {self.year}")

        if self.min_rating is not None and not (0 <= self.min_rating <= 5):
            raise ValueError("Minimum rating must be between 0 and 5")

        if self.max_rating is not None and not (0 <= self.max_rating <= 5):
            raise ValueError("Maximum rating must be between 0 and 5")

        if (self.min_rating is not None and 
            self.max_rating is not None and 
            self.min_rating > self.max_rating):
            raise ValueError("Minimum rating cannot be greater than maximum rating")

    def is_empty(self) -> bool:
        """Check if search criteria is empty"""
        return all(value is None for value in [
            self.title, self.genre, self.year, self.min_rating, self.max_rating,
            self.country, self.language, self.status
        ])

    def has_any_filters(self) -> bool:
        """Check if has any filters"""
        return not self.is_empty()

    def has_title_search(self) -> bool:
        """Check if has title search"""
        return self.title is not None and self.title.strip()

    def has_genre_filter(self) -> bool:
        """Check if has genre filter"""
        return self.genre is not None and self.genre.strip()

    def has_rating_filter(self) -> bool:
        """Check if has rating range filter"""
        return self.min_rating is not None or self.max_rating is not None

    def has_country_filter(self) -> bool:
        """Check if has country filter"""
        return self.country is not None and self.country.strip()

    def has_language_filter(self) -> bool:
        """Check if has language filter"""
        return self.language is not None and self.language.strip()

    def has_status_filter(self) -> bool:
        """Check if has status filter"""
        return self.status is not None and self.status.strip()

    def get_normalized_title(self) -> str:
        """Get normalized title for search"""
        return self.title.lower().strip() if self.title else ""

    def get_normalized_genre(self) -> str:
        """Get normalized genre for filter"""
        return self.genre.lower().strip() if self.genre else ""

    def get_normalized_country(self) -> str:
        """Get normalized country for filter"""
        return self.country.lower().strip() if self.country else ""

    def get_normalized_language(self) -> str:
        """Get normalized language for filter"""
        return self.language.lower().strip() if self.language else ""

    def get_normalized_status(self) -> str:
        """Get normalized status for filter"""
        return self.status.lower().strip() if self.status else ""

