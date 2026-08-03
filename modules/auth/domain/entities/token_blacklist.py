from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TokenBlacklist:

    id: str

    token: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )

    def is_valid(self) -> bool:
        # blacklist = toujours invalide
        return False