from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied
from modules.sav.domain.enums import TicketStatus
from modules.auth.domain.enums import UserRole

from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper
from modules.sav.application.ticket_chat_manager import TicketChatManager

class UpdateSupportTicketStatusUseCase:

    def __init__(self, repo, chat_manager: TicketChatManager):
        self.repo = repo
        self.chat_manager = chat_manager

    async def execute(self, ticket_id: str, status: TicketStatus, user):

        ticket = self.repo.get_by_id(ticket_id)

        if not ticket:
            raise SupportTicketNotFound()

        if user.role != UserRole.SAV_AGENT:
            raise TicketAccessDenied()

        # si même statut → no-op
        if ticket.status == status:
            return SupportTicketMapper.to_response(ticket)

        ticket.status = status
        ticket = self.repo.update(ticket)

        # =====================
        # WEBSOCKET BROADCAST
        # =====================
        await self.chat_manager.broadcast(
            ticket_id=ticket.id,
            payload={
                "type": "STATUS_UPDATED",
                "data": {
                    "ticket_id": ticket.id,
                    "status": ticket.status,
                }
            }
        )

        return SupportTicketMapper.to_response(ticket)