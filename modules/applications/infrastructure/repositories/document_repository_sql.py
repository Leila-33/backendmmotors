from sqlalchemy.orm import Session

from modules.applications.domain.repositories.document_repository import DocumentRepository

from modules.applications.domain.exceptions import DocumentNotFound
from modules.applications.infrastructure.db.document_model import DocumentModel

class DocumentRepositorySQL(DocumentRepository):

    def __init__(self, session: Session):

        self.session = session

    # =========================
    # GET BY APPLICATION + TYPE
    # =========================
    def get_by_application_and_type(
        self,
        application_id: str,
        doc_type: str
    ):

        return (
            self.session.query(DocumentModel)
            .filter_by(
                application_id=application_id,
                type=doc_type
            )
            .first()
        )

    # =========================
    # GET ALL BY APPLICATION
    # =========================
    def get_by_application(
        self,
        application_id: str
    ):

        return (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.application_id == application_id
            )
            .all()
        )

    # =========================
    # UPDATE STATUS
    # =========================
    def update_status(
        self,
        document_id: str,
        status: str,
        comment: str | None = None
    ):

        doc = (
            self.session.query(DocumentModel)
            .filter_by(id=document_id)
            .first()
        )

        if not doc:
            raise DocumentNotFound()

        doc.status = status

        if comment is not None:
            doc.comment = comment

        self.session.add(doc)

        self.session.flush()

        return doc

    # =========================
    # DELETE BY APPLICATION
    # =========================
    def delete_by_application(
        self,
        application_id: str
    ):

        (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.application_id == application_id
            )
            .delete(synchronize_session=False)
        )

    # =========================
    # COMMIT
    # =========================
    def commit(self):

        self.session.commit()