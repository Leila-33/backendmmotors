from dataclasses import dataclass


@dataclass
class CheckActivationTokenResult:
    first_name: str | None
    email: str
    already_verified: bool
    expired: bool