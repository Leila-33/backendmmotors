from dataclasses import dataclass


@dataclass
class RefreshTokensResult:
    access_token: str
    refresh_token: str