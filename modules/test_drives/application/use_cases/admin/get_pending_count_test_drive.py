class GetPendingTestDriveCountUseCase:

    def __init__(self, repository):
        self.repository = repository


    def execute(self):

        count = self.repository.count_pending()

        return {
            "count": count
        }