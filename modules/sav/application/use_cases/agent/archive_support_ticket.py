from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied, InvalidTicketState
from datetime import datetime, timezone
from modules.auth.domain.enums import UserRole
from modules.applications.domain.enums import EventType
from datetime import datetime, timezone
import logging


logger = logging.getLogger(__name__)


class ArchiveSupportTicketUseCase:

    def __init__(
        self,
        support_ticket_repository,
        event_service,
        unit_of_work,
    ):
        self.support_ticket_repository = support_ticket_repository
        self.event_service = event_service
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
            self.event_service.log(

    type=EventType.SUPPORT_TICKET_ARCHIVED,

    message="Ticket SAV archivé",

    application_id=ticket.application_id,

    user_id=user.id,

    event_metadata={

        "ticket_id": ticket.id,

        "status": ticket.status.value,

        "assigned_to": ticket.assigned_to,

        "ticket_owner": ticket.user_id,

    }
)

            self.unit_of_work.commit()
            
            logger.info(
    "Ticket SAV archivé",
    extra={
        "ticket_id": ticket.id,
        "admin_id": user.id,
    },
)
            return updated_ticket

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur archivage ticket SAV",
                extra={
                    "ticket_id": ticket_id,
                    "actor_id": user.id,
                },
            )

            raise