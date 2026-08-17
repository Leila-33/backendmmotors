from dataclasses import dataclass
from datetime import datetime

from modules.auth.domain.enums import UserRole


@dataclass
class UserListItemResult:
    id: str
    first_name: str
    last_name: str
    email: str
    role: UserRole
    is_active: bool
    is_deleted: bool
    is_verified: bool
    created_at: datetime


@dataclass
class FindUsersResult:
    items: list[UserListItemResult]
    page: int
    limit: int
    total: int
    pages: int