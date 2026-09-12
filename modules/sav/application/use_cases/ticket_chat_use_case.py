from modules.auth.domain.enums import UserRole
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketAccessDenied
)
from modules.sav.application.dtos.create_ticket_message_dto import CreateTicketMessageDTO


class TicketChatUseCase:

    def __init__(
        self,
        ticket_repository,
        create_message_uc,
        chat_manager,
        connection_manager,
    ):
        self.ticket_repository = ticket_repository
        self.create_message_uc = create_message_uc
        self.chat_manager = chat_manager
        self.connection_manager = connection_manager

    # =====================================================
    # CHECK ACCESS
    # =====================================================

    def check_access(
        self,
        ticket_id: str,
        user_id: str,
        user_role: UserRole,
    ):
        ticket = self.ticket_repository.get_by_id(ticket_id)

        if not ticket:
            raise SupportTicketNotFound()

        if (
            user_role not in (
                UserRole.ADMIN,
                UserRole.SAV_AGENT,
            )
            and ticket.user_id != user_id
        ):
            raise TicketAccessDenied()

        return ticket

    # =====================================================
    # SEND MESSAGE
    # =====================================================

    def send_message(
        self,
        dto: CreateTicketMessageDTO,
        user_id: str,
        user_role: UserRole,
    ):
        ticket = self.check_access(
            ticket_id=dto.ticket_id,
            user_id=user_id,
            user_role=user_role,
        )

        result = self.create_message_uc.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )

        return ticket, result.message

    # =====================================================
    # UNREAD
    # =====================================================

    def get_recipient(
        self,
        ticket,
        sender_id: str,
    ):
        if sender_id == ticket.user_id:
            # Le message vient du client
            if ticket.assigned_to:
                return ticket.assigned_to, UserRole.SAV_AGENT

            return None

        # Le message vient d'un agent SAV
        return ticket.user_id, UserRole.CLIENT