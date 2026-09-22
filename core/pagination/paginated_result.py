import math
from dataclasses import dataclass
from typing import Generic, TypeVar


import math



T = TypeVar("T")


@dataclass
class PaginatedResult(Generic[T]):

    items: list[T]

    total: int

    page: int

    limit: int

    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        limit: int,
    ) -> "PaginatedResult[T]":

        total_pages = (
            math.ceil(total / limit)
            if limit > 0
            else 0
        )

        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
        )