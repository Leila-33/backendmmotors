import uuid

from modules.applications.domain.entities.document import (
    Document,
    DocumentStatus,
    DocumentType
)

from modules.applications.domain.entities.application import (
    Application,
    ApplicationStatus
)

from modules.applications.api.schemas import UploadDocumentRequest
from modules.applications.api.schemas import UploadDocumentWithDraftRequest

class UploadDocument:

    def __init__(self, repo):
        self.repo = repo

    def execute(
        self,
        user_id: str,
        application_id: str,
        data: UploadDocumentRequest
    ):

        # 🔹 1. Récupérer application
        application = self.repo.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        # 🔐 sécurité : vérifier propriétaire
        if application.user_id != user_id:
            raise Exception("FORBIDDEN")

        # 🔹 2. Vérifier statut
        if application.status != ApplicationStatus.DRAFT:
            raise Exception("APPLICATION_NOT_EDITABLE")

        # 🔹 3. Créer document
        document = Document(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type=DocumentType(data.type.value),
            file_url=data.file_url,
            status=DocumentStatus.PENDING,
            comment=None
        )

        self.repo.save_document(document)

        # 🔹 4. Lier document à application
        application.document_ids.append(document.id)
        self.repo.update(application)

        # 🔹 5. Response
        return document
    
    def execute_with_draft(
        self,
        user_id: str,
        data: UploadDocumentWithDraftRequest
    ):

        # 🔹 1. Créer application (avec véhicule obligatoire)
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

        self.repo.save(application)

        # 🔹 2. Créer document
        document = Document(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type=DocumentType(data.type.value),
            file_url=data.file_url,
            status=DocumentStatus.PENDING,
            comment=None
        )

        self.repo.save_document(document)

        # 🔹 3. Lier document
        application.document_ids.append(document.id)
        self.repo.update(application)

        # 🔹 4. Response
        return document