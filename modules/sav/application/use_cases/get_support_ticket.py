from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied
from modules.auth.domain.enums import UserRole
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper
from datetime import datetime, timezone

from datetime import datetime, timezone

class GetSupportTicketUseCase:

    def __init__(self, repo, read_state_repo, connection_manager):
        self.repo = repo
        self.read_state_repo = read_state_repo
        self.connection_manager = connection_manager

    async def execute(self, ticket_id: str, user):

        ticket = self.repo.get_by_id(ticket_id)

        if not ticket:
            raise SupportTicketNotFound()

        if user.role != UserRole.SAV_AGENT and ticket.user_id != user.id:
            raise TicketAccessDenied()

        # =====================
        # MARK AS READ
        # =====================
        self.read_state_repo.mark_last_read(
            ticket_id=ticket_id,
            user_id=user.id,
            last_read_at=datetime.now(timezone.utc)
        )

        # =====================
        # REFRESH UNREAD COUNT (IMPORTANT)
        # =====================
        unread_count = self.repo.count_unread(user)

        # =====================
        # WEBSOCKET EVENT
        # =====================
        await self.connection_manager.send(
            user.id,
            {
                "type": "UNREAD_UPDATED",
                "count": unread_count
            }
        )

        return SupportTicketMapper.to_response(ticket)