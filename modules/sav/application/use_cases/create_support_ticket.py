from uuid import uuid4
from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.domain.enums import TicketStatus
from datetime import datetime, timezone
from modules.auth.domain.enums import UserRole
from modules.applications.domain.enums import EventType

class CreateSupportTicketUseCase:

    def __init__(
        self,
        repo,
        message_repo,
        assignment_service,
        event_service,
        unit_of_work,
    ):
        self.repo = repo
        self.message_repo = message_repo
        self.assignment_service = assignment_service
        self.event_service = event_service
        self.uow = unit_of_work


    def execute(
        self,
        user_id: str,
        user_role: UserRole,
        payload
    ):

        try:

            # =========================
            # ASSIGN AGENT
            # =========================

            agent = (
                self.assignment_service
                .get_next_agent()
            )


            # =========================
            # CREATE TICKET
            # =========================

            ticket = SupportTicket(

                id=str(uuid4()),

                user_id=user_id,

                application_id=(
                    payload.application_id
                    if payload.application_id
                    else None
                ),

                subject=payload.subject,

                description=payload.message,

                category=payload.category,

                status=TicketStatus.OPEN,

                priority=payload.priority,

                assigned_to=(
                    agent.id
                    if agent
                    else None
                ),

                created_at=datetime.now(timezone.utc)
            )


            saved_ticket = self.repo.create(ticket)


            # =========================
            # CREATE FIRST MESSAGE
            # =========================

            message = TicketMessage(

                id=str(uuid4()),

                ticket_id=saved_ticket.id,

                sender_id=user_id,

                sender_role=user_role,

                message=payload.message,

                created_at=datetime.now(timezone.utc)
            )


            self.message_repo.create(message)

            self.event_service.log(

                type=EventType.SUPPORT_TICKET_CREATED,

                message="Ticket SAV créé",

                application_id=saved_ticket.application_id,

                user_id=user_id,

                event_metadata={

                    "ticket_id": saved_ticket.id,

                    "subject": saved_ticket.subject,

                    "category": saved_ticket.category.value,

                    "priority": saved_ticket.priority.value,

                    "assigned_to": saved_ticket.assigned_to,

                }
            )
            # =========================
            # COMMIT
            # =========================
            self.uow.commit()


            return saved_ticket


        except Exception:

            # =========================
            # ROLLBACK
            # =========================
            self.uow.rollback()

            raise