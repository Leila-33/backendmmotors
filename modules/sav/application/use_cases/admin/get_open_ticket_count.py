class GetOpenTicketCountUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self):
        count = self.repo.count_open()
        return {"count": count}