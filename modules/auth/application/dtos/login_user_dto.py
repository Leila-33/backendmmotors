from dataclasses import dataclass


@dataclass
class LoginUserDTO:
    email: str
    password: str