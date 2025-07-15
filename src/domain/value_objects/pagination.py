"""
Pagination Value Objects - Domain Layer
Contains pagination-related value objects
"""
from dataclasses import dataclass
from typing import Generic, TypeVar, List

T = TypeVar('T')


@dataclass(frozen=True)
class PaginationParams:
    """
    PaginationParams Value Object
    Represents pagination parameters with validation
    """
    page: int
    limit: int

    def __post_init__(self):
        """Validation rules for pagination parameters"""
        if self.page < 1:
            raise ValueError("Page number must be greater than 0")
        
        if self.limit < 1:
            raise ValueError("Limit must be greater than 0")
        
        if self.limit > 100:
            raise ValueError("Limit cannot exceed 100")

    @property
    def offset(self) -> int:
        """Calculate offset for database queries"""
        return (self.page - 1) * self.limit

    def is_first_page(self) -> bool:
        """Check if this is the first page"""
        return self.page == 1

    def get_next_page(self) -> 'PaginationParams':
        """Get next page parameters"""
        return PaginationParams(page=self.page + 1, limit=self.limit)

    def get_previous_page(self) -> 'PaginationParams':
        """Get previous page parameters"""
        if self.is_first_page():
            raise ValueError("Cannot get previous page from first page")
        return PaginationParams(page=self.page - 1, limit=self.limit)


@dataclass(frozen=True)
class PaginatedResult(Generic[T]):
    """
    PaginatedResult Value Object
    Represents a paginated result set with metadata
    """
    data: List[T]
    total: int
    page: int
    limit: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        return (self.total + self.limit - 1) // self.limit

    @property
    def has_next(self) -> bool:
        """Check if there is a next page"""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page"""
        return self.page > 1

    @property
    def start_index(self) -> int:
        """Get the starting index of current page items"""
        return (self.page - 1) * self.limit + 1 if self.data else 0

    @property
    def end_index(self) -> int:
        """Get the ending index of current page items"""
        return min(self.page * self.limit, self.total) if self.data else 0 