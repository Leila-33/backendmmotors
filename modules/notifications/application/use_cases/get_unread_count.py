from modules.notifications.application.dtos.get_unread_count_dto import (
    GetUnreadCountDTO,
)

from modules.notifications.application.results.get_unread_count_result import (
    GetUnreadCountResult,
)


class GetUnreadCountUseCase:

    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    def execute(
        self,
        dto: GetUnreadCountDTO,
    ) -> GetUnreadCountResult:

        count = (
            self.repository
            .count_unread(
                dto.user_id
            )
        )

        return GetUnreadCountResult(
            count=count
        )