from dataclasses import dataclass

from modules.auth.domain.enums import UserRole


@dataclass
class UpdateUserRoleDTO:

    role: UserRole