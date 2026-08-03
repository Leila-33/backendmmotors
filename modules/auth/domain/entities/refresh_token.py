from dataclasses import dataclass, field
from datetime import datetime, timezone
from modules.auth.domain.enums import UserRole



@dataclass
class RefreshToken:

    id: str

    user_id: str

    jti: str

    role: UserRole

    expires_at: datetime

    revoked: bool = False

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )