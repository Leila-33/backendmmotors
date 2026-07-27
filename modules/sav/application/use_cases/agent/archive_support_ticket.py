from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied, InvalidTicketState
from datetime import datetime, timezone
from modules.auth.domain.enums import UserRole

from datetime import datetime, timezone


class ArchiveSupportTicketUseCase:

    def __init__(
        self,
        support_ticket_repository,
        unit_of_work,
    ):
        self.support_ticket_repository = support_ticket_repository
        self.unit_of_work = unit_of_work

    def execute(self, ticket_id: str, user):

        ticket = self.support_ticket_repository.get_by_id(
            ticket_id
        )

        if not ticket:
            raise SupportTicketNotFound()

        if user.role != UserRole.SAV_AGENT:
            raise TicketAccessDenied()

        if ticket.status not in (
            TicketStatus.RESOLVED,
            TicketStatus.CLOSED,
        ):
            raise InvalidTicketState()

        # Déjà archivé → opération idempotente
        if ticket.archived_at is not None:
            return ticket

        ticket.archived_at = datetime.now(timezone.utc)

        try:

            updated_ticket = self.support_ticket_repository.update(
                ticket
            )

            self.unit_of_work.commit()

            return updated_ticket

        except Exception:

            self.unit_of_work.rollback()

            raise