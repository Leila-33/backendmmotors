from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketClosedException,
    EmptyMessageException,
    MessageTooLongException
)
from uuid import uuid4
from modules.sav.domain.entities.ticket_message import TicketMessage

from modules.sav.domain.enums import TicketStatus

class CreateTicketMessageUseCase:

    def __init__(
        self,
        ticket_repo,
        message_repo,
        read_state_repo,
    ):
        self.ticket_repo = ticket_repo
        self.message_repo = message_repo
        self.read_state_repo = read_state_repo

    def execute(self, ticket_id: str, user, payload):

        # =====================
        # 1. LOAD TICKET
        # =====================
        ticket = self.ticket_repo.get_by_id(ticket_id)

        if not ticket:
            raise SupportTicketNotFound()

        # =====================
        # 2. BUSINESS RULES
        # =====================
        if ticket.status == TicketStatus.CLOSED:
            raise TicketClosedException()

        content = payload.message.strip()

        if not content:
            raise EmptyMessageException()

        if len(content) > 2000:
            raise MessageTooLongException()

        # =====================
        # 3. CREATE DOMAIN MESSAGE
        # =====================
        message = TicketMessage(
            id=str(uuid4()),
            ticket_id=ticket_id,
            sender_id=user.id,
            sender_role=user.role,
            message=content,
        )

        # =====================
        # 4. SAVE MESSAGE
        # =====================
        message = self.message_repo.create(message)

        # =====================
        # 5. MARK SENDER AS READ
        # =====================
        self.read_state_repo.mark_last_read(
            ticket_id=ticket_id,
            user_id=user.id,
            last_read_at=message.created_at,
        )

        return message