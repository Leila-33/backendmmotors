from dataclasses import dataclass
from datetime import datetime


@dataclass
class BlacklistedToken:
    token: str
    created_at: datetime

    def is_valid(self) -> bool:
        # blacklist = toujours invalide
        return False