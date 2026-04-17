import uuid
from modules.applications.domain.entities.application import Application, ApplicationStatus
from modules.applications.api.schemas import SubmitNewApplicationRequest
from datetime import datetime, timezone
from modules.applications.domain.entities.application_event import ApplicationEvent

class SubmitNewApplication:

    def __init__(self, repository, event_repo):
        self.repository = repository
        self.event_repo = event_repo

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

        now = datetime.now(timezone.utc)

        # 🔹 dates
        application.created_at = now
        application.submitted_at = now

        # 🔹 event CREATED
        event_created = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="CREATED",
            message="Dossier créé",
            created_at=now
        )

        # 🔹 event SUBMITTED
        event_submitted = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="SUBMITTED",
            message="Dossier soumis",
            created_at=now
        )

        self.event_repo.save(event_created)
        self.event_repo.save(event_submitted)
        application.status = ApplicationStatus.SUBMITTED

        # 🔹 3. Sauvegarde
        self.repository.save(application)
        # 🔹 4. Response métier (PAS Pydantic ici)
        return {
            "id": application.id,
            "status": application.status.value,
            "message": "Dossier soumis avec succès"
        }