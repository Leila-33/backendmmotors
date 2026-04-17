from modules.applications.domain.entities.application import ApplicationStatus
from datetime import datetime
from datetime import datetime, timezone
from modules.applications.domain.entities.application_event import ApplicationEvent
import uuid
from modules.applications.api.schemas import SubmitApplicationRequest



class SubmitApplication:

    def __init__(self, repository, event_repo):
            self.repository = repository
            self.event_repo = event_repo

    def execute(self, application_id: str, data: SubmitApplicationRequest):
        application = self.repository.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        if application.status != ApplicationStatus.DRAFT:
            raise Exception("APPLICATION_NOT_MODIFIABLE")

        # 🔹 UPDATE AVANT VALIDATION
        if data.monthly_income is not None:
            application.monthly_income = data.monthly_income

        if data.monthly_expenses is not None:
            application.monthly_expenses = data.monthly_expenses

        if data.employment_status is not None:
            application.employment_status = data.employment_status

        # 🔹 VALIDATION

        if not application.documents:
            raise Exception("DOCUMENTS_REQUIRED")

        required = {"identity", "rib", "payslip", "address_proof"}
        uploaded = {doc.type for doc in application.documents}

        missing = required - uploaded

        if missing:
            raise Exception(f"MISSING_DOCUMENTS:{','.join(missing)}")

        # 🔹 SUBMIT
        application.status = ApplicationStatus.SUBMITTED
        application.submitted_at = datetime.now(timezone.utc)
        self.repository.update(application)
        event = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="SUBMITTED",
            message="Dossier soumis",
            created_at=datetime.now(timezone.utc)
        )

        self.event_repo.save(event)
        return {
            "status": application.status.value,
            "message": "Dossier soumis avec succès"
        }