class GetTestDrivesAdminUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        status=None,
        search=None,
        page: int = 1,
        limit: int = 20
    ):

        return self.repository.get_all_admin(
            status=status,
            search=search,
            page=page,
            limit=limit
        )