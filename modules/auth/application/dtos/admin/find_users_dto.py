from dataclasses import dataclass
from modules.auth.domain.enums import (
    UserRole,
    UserStatusFilter
)


@dataclass
class FindUsersDTO:

    page: int = 1
    limit: int = 10

    search: str | None = None

    role: UserRole | None = None

    status: UserStatusFilter | None = None

    sort: str = "created_at_desc"