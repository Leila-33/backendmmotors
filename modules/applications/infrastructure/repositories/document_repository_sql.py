from sqlalchemy.orm import Session
from modules.applications.domain.repositories.document_repository import DocumentRepository
from modules.applications.infrastructure.db.document_model import DocumentModel
from modules.applications.infrastructure.mappers.document_mapper import (
    DocumentMapper
)
from modules.applications.domain.enums import (
    DocumentType,
    DocumentStatus
)
from modules.applications.domain.entities.document import (
    Document
)
from modules.applications.domain.exceptions import DocumentNotFound

class DocumentRepositorySQL(DocumentRepository):

    def __init__(
        self,
        session: Session
    ):
        self.session = session


    # =========================
    # CREATE
    # =========================

    def create(
        self,
        document: Document
    ) -> Document:

        model = DocumentMapper.to_model(
            document
        )

        self.session.add(model)

        self.session.flush()

        return DocumentMapper.to_domain(
            model
        )


    # =========================
    # GET BY APPLICATION + TYPE
    # =========================

    def get_by_application_and_type(
        self,
        application_id: str,
        doc_type: DocumentType,
    ) -> Document | None:


        model = (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.application_id == application_id,
                DocumentModel.type == doc_type,
            )
            .first()
        )


        return (
            DocumentMapper.to_domain(model)
            if model
            else None
        )


    # =========================
    # GET ALL
    # =========================

    def get_by_application(
        self,
        application_id: str,
    ) -> list[Document]:


        models = (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.application_id == application_id
            )
            .all()
        )


        return [
            DocumentMapper.to_domain(model)
            for model in models
        ]


    # =========================
    # GET BY ID
    # =========================

    def get_by_id(
        self,
        document_id: str,
    ) -> Document | None:


        model = (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.id == document_id
            )
            .first()
        )


        return (
            DocumentMapper.to_domain(model)
            if model
            else None
        )



    # =========================
    # SAVE / UPDATE
    # =========================

    def save(
        self,
        document: Document
    ) -> Document:


        model = (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.id == document.id
            )
            .first()
        )


        if model:

            DocumentMapper.update_model(
                model,
                document
            )

        else:

            model = DocumentMapper.to_model(
                document
            )

            self.session.add(model)


        self.session.flush()


        return DocumentMapper.to_domain(
            model
        )

    # =========================
    # UPDATE STATUS
    # =========================
    def update_status(
        self,
        document_id: str,
        status: DocumentStatus,
        comment: str | None = None,
    ) -> Document:

        model = (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.id == document_id
            )
            .first()
        )

        if not model:
            raise DocumentNotFound()

        model.status = status

        if comment is not None:
            model.comment = comment

        self.session.flush()

        return DocumentMapper.to_domain(
            model
        )

    # =========================
    # DELETE
    # =========================

    def delete(
        self,
        document_id: str
    ):

        self.session.query(DocumentModel)\
            .filter(
                DocumentModel.id == document_id
            )\
            .delete(
                synchronize_session=False
            )


        self.session.flush()



    # =========================
    # DELETE BY APPLICATION
    # =========================

    def delete_by_application(
        self,
        application_id: str,
    ) -> None:


        (
            self.session.query(DocumentModel)
            .filter(
                DocumentModel.application_id == application_id
            )
            .delete(
                synchronize_session=False
            )
        )


        self.session.flush()