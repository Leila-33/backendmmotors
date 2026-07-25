from dataclasses import dataclass, field
from modules.auth.domain.enums import UserRole
from datetime import datetime, timezone
from typing import Optional

@dataclass
class User:
    id: str
    first_name: str
    last_name: str
    email: str
    password: str
    role: UserRole = UserRole.CLIENT
    is_verified: bool = False
    is_active: bool = True
    accepted_cgu: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(
    default_factory=lambda: datetime.now(timezone.utc)
)
    def activate(
        self,
        hashed_password: str
    ):

        self.password = hashed_password

        self.is_verified = True

        self.is_active = True

        self.accepted_cgu = True
