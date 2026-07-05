from dataclasses import dataclass, field
from modules.core.enums import UserRole
from datetime import datetime
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
    created_at: datetime = field(default_factory=datetime.utcnow)
