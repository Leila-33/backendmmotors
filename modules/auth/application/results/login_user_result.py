from dataclasses import dataclass


@dataclass
class LoginUserResult:
    access_token: str
    refresh_token: str