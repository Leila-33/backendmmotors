from dataclasses import dataclass


@dataclass
class ActivateAccountResult:
    access_token: str
    refresh_token: str
    redirect: strs