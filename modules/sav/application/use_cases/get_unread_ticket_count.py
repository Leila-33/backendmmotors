from modules.sav.application.results.unread_ticket_count_result import (
    UnreadTicketCountResult,
)


class GetUnreadTicketCountUseCase:

    def __init__(
        self,
        support_ticket_repository,
    ):
        self.support_ticket_repository = (
            support_ticket_repository
        )

    def execute(
        self,
        user_id: str,
        user_role,
    ) -> UnreadTicketCountResult:

        count = (
            self.support_ticket_repository
            .count_unread(
                user_id=user_id,
                user_role=user_role,
            )
        )

        return UnreadTicketCountResult(
            count=count
        )