from datetime import datetime, timezone

from modules.auth.domain.enums import UserRole

from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketAccessDenied,
)

from modules.sav.application.dtos.get_support_ticket_dto import (
    GetSupportTicketDTO,
)

from modules.sav.application.results.get_support_ticket_result import (
    GetSupportTicketResult,
)


class GetSupportTicketUseCase:
    """
    Récupère le détail d'un ticket SAV après vérification
    des droits d'accès de l'utilisateur et marque le ticket
    comme lu pour celui-ci.
    """
    def __init__(
        self,
        ticket_repository,
        read_state_repository,
        unit_of_work,
    ):
        self.ticket_repository = (
            ticket_repository
        )

        self.read_state_repository = (
            read_state_repository
        )

        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: GetSupportTicketDTO,
    ) -> GetSupportTicketResult:

        # =========================
        # GET TICKET
        # =========================

        ticket = (
            self.ticket_repository
            .get_by_id(
                dto.ticket_id
            )
        )

        if ticket is None:
            raise SupportTicketNotFound()

        # =========================
        # ACCESS CONTROL
        # =========================

        allowed_roles = (
            UserRole.ADMIN,
            UserRole.SAV_AGENT,
        )

        if (
            dto.user_role not in allowed_roles
            and ticket.user_id != dto.user_id
        ):
            raise TicketAccessDenied()

        # =========================
        # MARK AS READ
        # =========================

        self.read_state_repository.mark_last_read(
            ticket_id=ticket.id,
            user_id=dto.user_id,
            last_read_at=datetime.now(
                timezone.utc
            ),
        )

        # =========================
        # COMMIT
        # =========================

        self.unit_of_work.commit()
        
        # =========================
        # UNREAD COUNT
        # =========================

        unread_count = self.ticket_repository.count_unread(
    user_id=dto.user_id,
    user_role=dto.user_role,
)
        # =========================
        # RESULT
        # =========================

        return GetSupportTicketResult(
            ticket=ticket,
            unread_count=unread_count,
        )