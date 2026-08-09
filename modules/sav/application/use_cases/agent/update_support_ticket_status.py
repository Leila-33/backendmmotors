from modules.sav.domain.exceptions import SupportTicketNotFound, TicketAccessDenied
from modules.sav.domain.enums import TicketStatus
from modules.auth.domain.enums import UserRole
from modules.sav.application.ticket_chat_manager import TicketChatManager
from modules.sav.infrastructure.mappers.support_ticket_mapper import SupportTicketMapper
from modules.applications.domain.enums import EventType
import logging


logger = logging.getLogger(__name__)

class UpdateSupportTicketStatusUseCase:

    def __init__(
        self,
        repo,
        chat_manager: TicketChatManager,
        event_service,
        unit_of_work,
    ):
        self.repo = repo
        self.chat_manager = chat_manager
        self.event_service = event_service
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


            self.event_service.log(

                type=EventType.SUPPORT_TICKET_STATUS_CHANGED,

                message="Statut du ticket SAV modifié",

                application_id=updated_ticket.application_id,

                user_id=user.id,

                event_metadata={

                    "ticket_id": updated_ticket.id,

                    "old_status": (
                        old_status.value
                        if old_status
                        else None
                    ),

                    "new_status": (
                        updated_ticket.status.value
                    ),

                    "ticket_owner": (
                        updated_ticket.user_id
                    ),

                    "assigned_to": (
                        updated_ticket.assigned_to
                    ),
                }
            )
            # =====================
            # COMMIT DATABASE
            # =====================

            self.uow.commit()

            logger.info(
    "Statut ticket SAV modifié",
    extra={
        "ticket_id": ticket.id,
        "actor_id": user.id,
        "old_status": old_status.value,
        "new_status": status.value,
    },
)

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

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur modification statut ticket SAV",
                extra={
                    "ticket_id": ticket_id,
                    "actor_id": user.id,
                },
            )

            raise