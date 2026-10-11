from modules.auth.domain.enums import UserRole
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketAccessDenied
)
from modules.sav.application.dtos.create_ticket_message_dto import CreateTicketMessageDTO
from datetime import datetime, timezone


class TicketChatUseCase:
    """
    Centralise les opérations métier du chat associé aux tickets SAV.

    Il vérifie l'accès au ticket, permet l'envoi de messages
    et détermine le destinataire d'un message selon son expéditeur.
    """
    def __init__(
        self,
        ticket_repository,
        create_message_uc,
        chat_manager,
        read_state_repository,
        unit_of_work,
    ):
        self.ticket_repository = ticket_repository
        self.create_message_uc = create_message_uc
        self.chat_manager = chat_manager
        self.read_state_repository = read_state_repository
        self.unit_of_work = unit_of_work

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

    def mark_as_read(
        self,
        ticket_id: str,
        user_id: str,
        user_role: UserRole,
    ) -> int:
        # Vérifier que l'utilisateur a accès au ticket.
        self.check_access(
            ticket_id=ticket_id,
            user_id=user_id,
            user_role=user_role,
        )

        # Enregistrer la dernière lecture.
        self.read_state_repository.mark_last_read(
            ticket_id=ticket_id,
            user_id=user_id,
            last_read_at=datetime.now(timezone.utc),
        )

        self.unit_of_work.commit()

        # Retourner le nombre de tickets encore non lus.
        return self.ticket_repository.count_unread(
            user_id=user_id,
            user_role=user_role,
        )