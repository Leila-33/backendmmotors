from dataclasses import dataclass
from datetime import datetime
from modules.core.enums import UserRole


@dataclass
class RefreshTokenEntity:
    id: str
    user_id: str
    role: UserRole
    jti: str

    expires_at: datetime
    created_at: datetime

    revoked: bool = False