from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserActivationToken:

    id: str

    user_id: str

    token_hash: str
    
    quote_id: str | None


    expires_at: datetime

    used_at: Optional[datetime] = None

    created_at: Optional[datetime] = None


    def is_used(self) -> bool:

        return self.used_at is not None



    def is_expired(
        self,
        now: datetime
    ) -> bool:

        return self.expires_at < now



    def consume(
        self,
        now: datetime
    ) -> None:

        self.used_at = now