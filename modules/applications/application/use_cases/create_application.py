
from modules.applications.api.schemas import CreateApplicationRequest
import uuid
from modules.applications.domain.entities.application import Application, ApplicationStatus


class CreateApplication:

    def __init__(self, repo, user_repo, vehicle_repo):
        self.repo = repo
        self.user_repo = user_repo
        self.vehicle_repo = vehicle_repo

    def execute(self, data: CreateApplicationRequest, user_id: str):

        # 🔹 1. Validation user (optionnelle)
        if self.user_repo:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                raise Exception("USER_NOT_FOUND")

        # 🔹 2. Validation véhicule
        if self.vehicle_repo:
            vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)
            if not vehicle:
                raise Exception("VEHICLE_NOT_FOUND")

            if not vehicle.isAvailable:
                raise Exception("VEHICLE_NOT_AVAILABLE")

        # 🔹 3. Création du dossier
        application = Application(
            id=str(uuid.uuid4()),

            user_id=user_id,  # 🔥 SECURISÉ
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