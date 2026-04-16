import uuid
from modules.applications.domain.entities.application import Application, ApplicationStatus
from modules.applications.domain.entities.document import Document, DocumentStatus


class CreateApplicationWithDocument:

    def __init__(self, application_repo, document_repo, vehicle_repo):
        self.application_repo = application_repo
        self.document_repo = document_repo
        self.vehicle_repo = vehicle_repo

    def execute(self, user_id: str, data):

        # 🔹 1. vérifier véhicule
        vehicle = self.vehicle_repo.get_by_id(data.vehicle_id)

        if not vehicle:
            raise Exception("VEHICLE_NOT_FOUND")

        if not vehicle.is_available:
            raise Exception("VEHICLE_NOT_AVAILABLE")

        # 🔹 2. créer application (DRAFT)
        application = Application(
            id=str(uuid.uuid4()),
            user_id=user_id,
            vehicle_id=data.vehicle_id,
            monthly_income=None,
            monthly_expenses=None,
            employment_status=None,
            status=ApplicationStatus.DRAFT,
            document_ids=[]
        )

        self.application_repo.save(application)

        # 🔹 3. créer document
        document = Document(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type=data.type,
            file_url=str(data.file_url),
            status=DocumentStatus.PENDING,
            comment=None
        )

        self.document_repo.save(document)

        # 🔹 4. lier document à application
        application.document_ids.append(document.id)
        self.application_repo.update(application)

        # 🔹 4. Response
        return document