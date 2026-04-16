from modules.applications.domain.entities.application import ApplicationStatus
from modules.applications.api.schemas import UpdateApplicationRequest


class UpdateApplication:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, application_id: str, data: UpdateApplicationRequest):

        # 🔹 1. Get application
        application = self.repository.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        # 🔹 2. Check if editable
        if application.status != ApplicationStatus.DRAFT:
            raise Exception("APPLICATION_NOT_EDITABLE")

        # 🔹 3. Update fields (seulement ceux fournis)
        update_data = data.model_dump(exclude_none=True)

        for key, value in update_data.items():
            if hasattr(application, key):
                setattr(application, key, value)

        # 🔹 4. Save
        self.repository.update(application)

        # 🔹 5. Response
        return {
            "message": "Dossier mis à jour avec succès"
        }