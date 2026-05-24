class GetNotificationsUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: str):

        notifications = self.repository.get_by_user_id(user_id)

        return [
            {
                "id": n.id,
                "title": n.title,
                "message": n.message,
                "type": n.type.value,
                "status": n.status.value,
                "created_at": n.created_at,
                "application_id": n.application_id,
                "test_drive_id": n.test_drive_id,
                "document_id": n.document_id,
            }
            for n in notifications
        ]