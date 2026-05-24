class GetUnreadCountUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: str):

        return self.repository.count_unread(user_id)