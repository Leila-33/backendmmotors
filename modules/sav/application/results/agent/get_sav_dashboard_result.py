from dataclasses import dataclass
from datetime import datetime

from modules.sav.domain.enums import (
    TicketPriority,
    TicketStatus,
)


@dataclass(frozen=True)
class SavDashboardTicketResult:

    id: str
    subject: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime


@dataclass(frozen=True)
class GetSavDashboardResult:

    total: int
    open: int
    urgent: int
    recent_tickets: list[SavDashboardTicketResult]