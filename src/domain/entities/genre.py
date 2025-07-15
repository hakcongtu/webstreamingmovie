"""
Genre Entity - Domain Model
Represents a movie genre with its properties
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Genre:
    """
    Genre Entity - Immutable domain object
    Represents a movie genre with validation
    """
    name: str
    description: Optional[str] = None

    def __post_init__(self):
        """Domain validation rules"""
        self._validate()

    def _validate(self) -> None:
        """Validate domain rules"""
        if not self.name or not self.name.strip():
            raise ValueError("Genre name cannot be empty")
        
        if len(self.name) > 50:
            raise ValueError("Genre name cannot exceed 50 characters")

    def equals(self, other: 'Genre') -> bool:
        """Business logic: Compare genres"""
        return self.name.lower() == other.name.lower()

    def get_normalized_name(self) -> str:
        """Business logic: Get normalized name"""
        return self.name.lower().strip()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Genre(name='{self.name}')" 