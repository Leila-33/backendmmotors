from dataclasses import dataclass

from modules.auth.domain.enums import UserRole


@dataclass(frozen=True)
class GetSupportTicketDTO:

    ticket_id: str
    user_id: str
    user_role: UserRole