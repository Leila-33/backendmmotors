from dataclasses import dataclass

from modules.auth.domain.enums import UserRole


@dataclass
class CreateUserResult:
    id: str
    email: str
    role: UserRole