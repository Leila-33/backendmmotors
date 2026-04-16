import uuid
from modules.applications.domain.entities.application import Application, ApplicationStatus
from modules.applications.api.schemas import SubmitNewApplicationRequest


class SubmitNewApplication:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, data: SubmitNewApplicationRequest, user_id: str):

        # 🔹 1. Validation véhicule (métier)
        if not data.vehicle_id:
            raise Exception("VEHICLE_NOT_FOUND")

        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
        if not vehicle:
            raise Exception("VEHICLE_NOT_FOUND")
        if not vehicle.is_available:
            raise Exception("VEHICLE_NOT_AVAILABLE")

        # 🔹 2. Création application
        application = Application(
            id=str(uuid.uuid4()),
            user_id=user_id,
            vehicle_id=data.vehicle_id,
            monthly_income=data.monthly_income,
            monthly_expenses=data.monthly_expenses,
            employment_status=data.employment_status,
            status=ApplicationStatus.SUBMITTED,
            document_ids=[]
        )

        # 🔹 3. Sauvegarde
        self.repository.save(application)

        # 🔹 4. Response métier (PAS Pydantic ici)
        return {
            "id": application.id,
            "status": application.status.value,
            "message": "Dossier soumis avec succès"
        }