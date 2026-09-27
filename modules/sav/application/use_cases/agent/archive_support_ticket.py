from datetime import datetime, timezone
import logging

from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    InvalidTicketState,
)
from modules.applications.domain.enums import EventType

from modules.sav.application.dtos.agent.archive_support_ticket_dto import (
    ArchiveSupportTicketDTO,
)
from modules.sav.application.results.agent.archive_support_ticket_result import (
    ArchiveSupportTicketResult,
)


logger = logging.getLogger(__name__)


class ArchiveSupportTicketUseCase:
    """
    Archive un ticket SAV après vérification de son état.

    Seuls les tickets résolus ou clôturés peuvent être archivés.
    L'opération est idempotente et l'archivage est enregistré
    dans l'historique des événements.
    """
    def __init__(
        self,
        support_ticket_repository,
        event_service,
        unit_of_work,
    ):
        self.support_ticket_repository = (
            support_ticket_repository
        )

        self.event_service = event_service

        self.unit_of_work = unit_of_work


    def execute(
        self,
        dto: ArchiveSupportTicketDTO,
    ) -> ArchiveSupportTicketResult:

        ticket = None

        try:

            # =====================================
            # GET TICKET
            # =====================================

            ticket = (
                self.support_ticket_repository
                .get_by_id(
                    dto.ticket_id
                )
            )

            if not ticket:
                raise SupportTicketNotFound()


            # =====================================
            # BUSINESS RULE
            # =====================================

            if ticket.status not in (
                TicketStatus.RESOLVED,
                TicketStatus.CLOSED,
            ):
                raise InvalidTicketState()


            # =====================================
            # IDEMPOTENCE
            # =====================================

            if ticket.archived_at is not None:

                return ArchiveSupportTicketResult(
                    ticket=ticket
                )


            # =====================================
            # ARCHIVE
            # =====================================

            ticket.archived_at = (
                datetime.now(timezone.utc)
            )


            updated_ticket = (
                self.support_ticket_repository
                .update(ticket)
            )


            # =====================================
            # EVENT
            # =====================================

            self.event_service.log(

                type=EventType.SUPPORT_TICKET_ARCHIVED,

                message="Ticket SAV archivé",

                application_id=(
                    ticket.application_id
                ),

                user_id=dto.user_id,

                event_metadata={
                    "ticket_id": ticket.id,
                    "status": ticket.status.value,
                    "assigned_to": ticket.assigned_to,
                    "ticket_owner": ticket.user_id,
                },
            )


            # =====================================
            # COMMIT
            # =====================================

            self.unit_of_work.commit()


            # =====================================
            # LOG
            # =====================================

            logger.info(
                "Ticket SAV archivé",
                extra={
                    "ticket_id": ticket.id,
                    "actor_id": dto.user_id,
                },
            )


            return ArchiveSupportTicketResult(
                ticket=updated_ticket
            )


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur archivage ticket SAV",
                extra={
                    "ticket_id": dto.ticket_id,
                    "actor_id": dto.user_id,
                },
            )

            raise