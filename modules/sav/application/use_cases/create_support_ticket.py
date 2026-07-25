from uuid import uuid4
from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.sav.domain.enums import TicketStatus
from modules.sav.api.schemas import TicketMessageCreate
class CreateSupportTicketUseCase:

    def __init__(self, repo, message_repo, assignment_service):
        self.repo = repo
        self.message_repo = message_repo
        self.assignment_service = assignment_service

    def execute(self, user_id: str, user_role: str, payload: TicketMessageCreate):

        agent = self.assignment_service.get_next_agent()

        ticket = SupportTicket(
            id=str(uuid4()),
            user_id=user_id,
            application_id = payload.application_id or None,
            subject=payload.subject,
            description=payload.message,
            category=payload.category,
            status=TicketStatus.OPEN,
            priority=payload.priority,
            assigned_to=agent.id if agent else None
        )

        saved_ticket = self.repo.create(ticket)

        message = TicketMessage(
            id=str(uuid4()),
            ticket_id=saved_ticket.id,
            sender_id=user_id,
            sender_role=user_role,
            message=payload.message,
        )

        self.message_repo.create(message)

        return saved_ticket