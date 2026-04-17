import uuid
from modules.applications.domain.entities.document import Document, DocumentStatus
from modules.applications.domain.entities.application_event import ApplicationEvent
from datetime import datetime, timezone

class UploadDocument:

    def __init__(self, application_repo, document_repo, event_repo):
        self.application_repo = application_repo
        self.document_repo = document_repo
        self.event_repo = event_repo

    def execute(self, user_id: str, application_id: str, data):

        application = self.application_repo.get_by_id(application_id)

        if not application:
            raise Exception("APPLICATION_NOT_FOUND")

        if application.user_id != user_id:
            raise Exception("FORBIDDEN")

        if application.status != application.status.DRAFT:
            raise Exception("APPLICATION_NOT_EDITABLE")

        # 🔹 récupérer documents existants
        existing_documents = self.document_repo.get_by_application_id(application.id)

        existing_doc = next(
            (doc for doc in existing_documents if doc.type == data.type),
            None
        )

        if existing_doc:
            # 🔄 UPDATE (remplacement)
            existing_doc.file_url = str(data.file_url)
            existing_doc.status = DocumentStatus.PENDING
            existing_doc.comment = None

            self.document_repo.update(existing_doc)

            return existing_doc

        # 🔹 sinon créer nouveau
        document = Document(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type=data.type,
            file_url=str(data.file_url),
            status=DocumentStatus.PENDING,
            comment=None
        )

        self.document_repo.save(document)
        event = ApplicationEvent(
            id=str(uuid.uuid4()),
            application_id=application.id,
            type="DOCUMENT_ADDED",
            message=f"Document {document.type} ajouté",
            created_at=datetime.now(timezone.utc)
        )

        self.event_repo.save(event)

        application.document_ids.append(document.id)
        self.application_repo.update(application)

        return document