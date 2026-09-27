import logging
from datetime import datetime, timezone
from uuid import uuid4

from modules.auth.domain.enums import UserRole
from modules.applications.domain.enums import EventType

from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.domain.enums import TicketStatus

from modules.sav.application.dtos.create_support_ticket_dto import (
    CreateSupportTicketDTO,
)
from modules.sav.application.results.create_support_ticket_result import (
    CreateSupportTicketResult,
)
from modules.applications.domain.exceptions import ApplicationNotFound

logger = logging.getLogger(__name__)


class CreateSupportTicketUseCase:
    """
    Crée un ticket SAV à partir d'une demande utilisateur,
    vérifie éventuellement le dossier associé et attribue
    automatiquement le ticket à un agent disponible.

    Le premier message est créé avec le ticket et la création
    est enregistrée dans l'historique des événements.
    """
    def __init__(
        self,
        ticket_repository,
        message_repository,
        assignment_service,
        event_service,
        application_repository,
        unit_of_work,
    ):
        self.ticket_repository = ticket_repository
        self.message_repository = message_repository
        self.assignment_service = assignment_service
        self.event_service = event_service
        self.application_repository = (
            application_repository
        )
        self.unit_of_work = unit_of_work

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto: CreateSupportTicketDTO,
        user_id: str,
        user_role: UserRole,
    ) -> CreateSupportTicketResult:

        ticket = None

        try:

            # =================================================
            # APPLICATION
            # =================================================

            application_id = (
                dto.application_id.strip()
                if dto.application_id
                else None
            )

            application = None

            if application_id:

                application = (
                    self.application_repository
                    .get_by_id(application_id)
                )

                if application is None:
                    raise ApplicationNotFound()

            # =================================================
            # ASSIGN AGENT
            # =================================================

            agent = (
                self.assignment_service
                .get_next_agent()
            )

            assigned_to = (
                agent.id
                if agent
                else None
            )

            # =================================================
            # CREATE TICKET
            # =================================================

            ticket = SupportTicket(
                id=str(uuid4()),
                user_id=user_id,
                application_id=(
                    application.id
                    if application
                    else None
                ),
                subject=dto.subject.strip(),
                description=dto.message.strip(),
                category=dto.category,
                status=TicketStatus.OPEN,
                priority=dto.priority,
                assigned_to=assigned_to,
                created_at=datetime.now(
                    timezone.utc
                ),
            )

            ticket = (
                self.ticket_repository
                .create(ticket)
            )

            # =================================================
            # FIRST MESSAGE
            # =================================================

            message = TicketMessage(
                id=str(uuid4()),
                ticket_id=ticket.id,
                sender_id=user_id,
                sender_role=user_role,
                message=dto.message.strip(),
                created_at=datetime.now(
                    timezone.utc
                ),
            )

            self.message_repository.create(
                message
            )

            # =================================================
            # EVENT
            # =================================================

            self.event_service.log(
                type=EventType.SUPPORT_TICKET_CREATED,
                message="Ticket SAV créé",
                application_id=ticket.application_id,
                user_id=user_id,
                event_metadata={
                    "ticket_id": ticket.id,
                    "subject": ticket.subject,
                    "category": ticket.category.value,
                    "priority": ticket.priority.value,
                    "assigned_to": ticket.assigned_to,
                },
            )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # LOG
            # =================================================

            logger.info(
                "Ticket SAV créé",
                extra={
                    "ticket_id": ticket.id,
                    "user_id": user_id,
                    "assigned_to": ticket.assigned_to,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return CreateSupportTicketResult(
                ticket=ticket,
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création ticket SAV",
                extra={
                    "user_id": user_id,
                    "ticket_id": (
                        ticket.id
                        if ticket
                        else None
                    ),
                },
            )

            raise