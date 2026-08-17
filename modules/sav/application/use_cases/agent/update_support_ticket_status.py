import logging

from modules.sav.domain.enums import TicketStatus
from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
)

from modules.sav.application.dtos.agent.update_support_ticket_status_dto import (
    UpdateSupportTicketStatusDTO,
)

from modules.sav.application.results.agent.update_support_ticket_status_result import (
    UpdateSupportTicketStatusResult,
)

from modules.sav.application.ticket_chat_manager import (
    TicketChatManager,
)

from modules.applications.domain.enums import EventType


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
        dto: UpdateSupportTicketStatusDTO,
    ) -> UpdateSupportTicketStatusResult:

        ticket = None

        try:

            # =========================
            # GET TICKET
            # =========================

            ticket = self.repo.get_by_id(
                dto.ticket_id
            )

            if not ticket:
                raise SupportTicketNotFound()


            # =========================
            # NO CHANGE
            # =========================

            if ticket.status == dto.status:

                return UpdateSupportTicketStatusResult(
                    ticket=ticket,
                    old_status=ticket.status,
                )


            # =========================
            # OLD STATUS
            # =========================

            old_status = ticket.status


            # =========================
            # UPDATE
            # =========================

            ticket.status = dto.status

            updated_ticket = self.repo.update(
                ticket
            )


            # =========================
            # EVENT
            # =========================

            self.event_service.log(

                type=EventType.SUPPORT_TICKET_STATUS_CHANGED,

                message="Statut du ticket SAV modifié",

                application_id=(
                    updated_ticket.application_id
                ),

                user_id=dto.user_id,

                event_metadata={
                    "ticket_id": updated_ticket.id,

                    "old_status": (
                        old_status.value
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
                },
            )


            # =========================
            # COMMIT
            # =========================

            self.uow.commit()


            logger.info(
                "Statut ticket SAV modifié",
                extra={
                    "ticket_id": updated_ticket.id,
                    "actor_id": dto.user_id,
                    "old_status": old_status.value,
                    "new_status": dto.status.value,
                },
            )


            # =========================
            # WEBSOCKET
            # APRÈS COMMIT
            # =========================

            await self.chat_manager.broadcast(
                ticket_id=updated_ticket.id,
                payload={
                    "type": "STATUS_UPDATED",

                    "data": {
                        "ticket_id": updated_ticket.id,

                        "old_status": (
                            old_status.value
                        ),

                        "status": (
                            updated_ticket.status.value
                        ),
                    },
                },
            )


            return UpdateSupportTicketStatusResult(
                ticket=updated_ticket,
                old_status=old_status,
            )


        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur modification statut ticket SAV",
                extra={
                    "ticket_id": dto.ticket_id,
                    "actor_id": dto.user_id,
                },
            )

            raise