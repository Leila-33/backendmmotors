from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied, InvalidTicketState
from datetime import datetime, timezone
from modules.auth.domain.enums import UserRole

class ArchiveSupportTicketUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, ticket_id: str, user):

        ticket = self.repo.get_by_id(ticket_id)

        if not ticket:
            raise SupportTicketNotFound()

        if user.role != UserRole.SAV_AGENT:
            raise TicketAccessDenied()

        if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            raise InvalidTicketState()

        ticket.is_archived = True
        ticket.archived_at = datetime.now(timezone.utc)

        return self.repo.update(ticket)