from dataclasses import dataclass
from typing import Generic, TypeVar, List


T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):

    items: List[T]

    total: int

    page: int

    limit: int

    @property
    def total_pages(self) -> int:
        if self.limit == 0:
            return 0

        return (self.total + self.limit - 1) // self.limit