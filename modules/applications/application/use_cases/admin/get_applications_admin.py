class GetApplicationsAdmin:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, filters: dict, page: int, size: int):

        return self.repo.search_admin(filters, page, size)