
from modules.applications.api.schemas import CreateApplicationRequest
import uuid
from modules.applications.domain.entities.application import Application, ApplicationStatus

class CreateApplication:

    def __init__(self, repo, vehicle_repo):
        self.repo = repo
        self.vehicle_repo = vehicle_repo

    def execute(self, data: CreateApplicationRequest, user_id: str):

        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)

        if not vehicle:
            raise Exception("VEHICLE_NOT_FOUND")

        if not vehicle.is_available:
            raise Exception("VEHICLE_NOT_AVAILABLE")

        application = Application(
            id=str(uuid.uuid4()),
            user_id=user_id,
            vehicle_id=data.vehicle_id,
            monthly_income=data.monthly_income,
            monthly_expenses=data.monthly_expenses,
            employment_status=data.employment_status,
            status=ApplicationStatus.DRAFT,
            document_ids=[]
        )

        self.repo.save(application)

        return {
            "id": application.id,
            "status": application.status.value,
            "message": "Dossier créé avec succès en brouillon"
        }