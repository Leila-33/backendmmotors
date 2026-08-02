from modules.applications.domain.entities.document import Document
from modules.applications.api.schemas import DocumentResponse
from modules.applications.infrastructure.db.document_model import DocumentModel

class DocumentMapper:

    @staticmethod
    def to_domain(
        model: DocumentModel
    ) -> Document:

        return Document(
            id=model.id,
            application_id=model.application_id,
            type=model.type,
            s3_key=model.s3_key,
            status=model.status,
            comment=model.comment,
        )


    @staticmethod
    def to_model(
        entity: Document
    ) -> DocumentModel:

        return DocumentModel(
            id=entity.id,
            application_id=entity.application_id,
            type=entity.type,
            s3_key=entity.s3_key,
            status=entity.status,
            comment=entity.comment,
        )


    @staticmethod
    def update_model(
        model: DocumentModel,
        entity: Document
    ) -> DocumentModel:

        model.type = entity.type
        model.s3_key = entity.s3_key
        model.status = entity.status
        model.comment = entity.comment

        return model


    @staticmethod
    def to_response(
        document: Document
    ) -> DocumentResponse:

        return DocumentResponse(
            id=document.id,
            application_id=document.application_id,
            type=document.type,
            s3_key=document.s3_key,
            status=document.status,
            comment=document.comment,
        )