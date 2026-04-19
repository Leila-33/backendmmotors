class GetApplicationDetail:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, application_id: str):

        application = self.repo.get_detail(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        return application