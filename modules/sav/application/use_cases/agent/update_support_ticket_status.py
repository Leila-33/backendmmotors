from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied
from modules.sav.domain.enums import TicketStatus
from modules.auth.domain.enums import UserRole
from modules.sav.application.ticket_chat_manager import TicketChatManager

class UpdateSupportTicketStatusUseCase:

    def __init__(
        self,
        repo,
        chat_manager : TicketChatManager,
        unit_of_work
    ):
        self.repo = repo
        self.chat_manager = chat_manager
        self.uow = unit_of_work


    async def execute(
        self,
        ticket_id: str,
        status: TicketStatus,
        user
    ):

        # =====================
        # START TRANSACTION
        # =====================
        try:

            ticket = self.repo.get_by_id(ticket_id)


            if not ticket:
                raise SupportTicketNotFound()


            # =====================
            # SECURITY
            # =====================

            if user.role != UserRole.SAV_AGENT:
                raise TicketAccessDenied()



            # =====================
            # NO CHANGE
            # =====================

            if ticket.status == status:

                self.uow.rollback()

                return SupportTicketMapper.to_response(
                    ticket
                )



            old_status = ticket.status



            # =====================
            # UPDATE
            # =====================

            ticket.status = status


            updated_ticket = self.repo.update(
                ticket
            )



            # =====================
            # COMMIT DATABASE
            # =====================

            self.uow.commit()



        except Exception:

            self.uow.rollback()

            raise



        # =====================
        # WEBSOCKET AFTER COMMIT
        # =====================

        await self.chat_manager.broadcast(
            ticket_id=updated_ticket.id,
            payload={
                "type": "STATUS_UPDATED",

                "data": {
                    "ticket_id": updated_ticket.id,

                    "old_status": (
                        old_status.value
                        if old_status
                        else None
                    ),

                    "status": updated_ticket.status.value,
                }
            }
        )


        return updated_ticket