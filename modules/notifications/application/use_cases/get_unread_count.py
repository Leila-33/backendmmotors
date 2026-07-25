from modules.notifications.api.schemas import (
    UnreadNotificationCountResponse
)

class GetUnreadCountUseCase:

    def __init__(
        self,
        repository,
    ):
        self.repository = repository


    def execute(
        self,
        user_id: str,
    ):

        count = (
            self.repository
            .count_unread(user_id)
        )


        return UnreadNotificationCountResponse(
            count=count
        )