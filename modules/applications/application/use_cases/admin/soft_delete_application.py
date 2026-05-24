class SoftDeleteApplicationUseCase:

    def __init__(self, application_repository):
        self.application_repository = application_repository

    def execute(self, application_id: str):

        self.application_repository.soft_delete(application_id)

        return {"success": True}