from infrastructure.db.session import SessionLocal
from modules.applications.infrastructure.db.models import DocumentModel
from modules.applications.domain.entities.document import Document


class DocumentRepositorySQL:

    def save(self, document: Document):
        db = SessionLocal()
        try:
            model = DocumentModel(
                id=document.id,
                application_id=document.application_id,
                type=document.type.value,
                file_url=document.file_url,
                status=document.status.value,
                comment=document.comment
            )

            db.add(model)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    def get_by_application_id(self, application_id: str):
        db = SessionLocal()
        try:
            return db.query(DocumentModel).filter(
                DocumentModel.application_id == application_id
            ).all()

        finally:
            db.close()