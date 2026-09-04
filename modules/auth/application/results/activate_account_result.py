from dataclasses import dataclass


@dataclass
class ActivateAccountResult:
    message: str
    access_token: str
    refresh_token: str
    redirect: str