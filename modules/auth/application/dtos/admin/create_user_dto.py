from dataclasses import dataclass

from modules.auth.domain.enums import UserRole


@dataclass
class CreateUserDTO:

    first_name: str
    last_name: str
    email: str
    password: str
    role: UserRole