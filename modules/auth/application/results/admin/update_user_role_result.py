from dataclasses import dataclass

from modules.auth.domain.enums import UserRole


@dataclass
class UpdateUserRoleResult:
    id: str
    role: UserRole