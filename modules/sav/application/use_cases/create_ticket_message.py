from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketClosedException,
    EmptyMessageException,
    MessageTooLongException
)
from uuid import uuid4
from modules.sav.domain.entities.ticket_message import TicketMessage
from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden
from modules.sav.domain.enums import TicketStatus
from datetime import datetime, timezone

class CreateTicketMessageUseCase:

    def __init__(
        self,
        ticket_repo,
        message_repo,
        read_state_repo,
        unit_of_work
    ):
        self.ticket_repo = ticket_repo
        self.message_repo = message_repo
        self.read_state_repo = read_state_repo
        self.uow = unit_of_work


    def execute(
        self,
        ticket_id: str,
        user,
        payload
    ):

        try:

            # =====================
            # 1. LOAD TICKET
            # =====================
            ticket = self.ticket_repo.get_by_id(ticket_id)

            if not ticket:
                raise SupportTicketNotFound()


            # =====================
            # 2. SECURITY
            # =====================
            if (
                ticket.user_id != user.id
                and user.role not in [
                    UserRole.ADMIN,
                    UserRole.SAV_AGENT
                ]
            ):
                raise Forbidden()


            # =====================
            # 3. BUSINESS RULES
            # =====================
            if ticket.status == TicketStatus.CLOSED:
                raise TicketClosedException()


            content = payload.message.strip()


            if not content:
                raise EmptyMessageException()


            if len(content) > 2000:
                raise MessageTooLongException()



            # =====================
            # 4. CREATE MESSAGE
            # =====================
            message = TicketMessage(
                id=str(uuid4()),
                ticket_id=ticket_id,
                sender_id=user.id,
                sender_role=user.role,
                message=content,
                created_at=datetime.now(timezone.utc)   # ajout ici
            )


            saved_message = self.message_repo.create(
                message
            )


            # =====================
            # 5. READ STATE
            # =====================
            self.read_state_repo.mark_last_read(
                ticket_id=ticket_id,
                user_id=user.id,
                last_read_at=saved_message.created_at
            )


            # =====================
            # 6. UPDATE TICKET DATE
            # =====================
            ticket.updated_at = datetime.now(timezone.utc)

            self.ticket_repo.update(ticket)


            self.uow.commit()


            return saved_message


        except Exception:

            self.uow.rollback()
            raise