from dataclasses import dataclass
from modules.core.enums import UserRole


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