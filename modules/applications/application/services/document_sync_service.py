from modules.applications.domain.repositories.document_repository import DocumentRepository
from modules.applications.application.dtos.document_dto import DocumentDTO
from uuid import uuid4
from modules.applications.domain.enums import (
    DocumentStatus
)
from modules.applications.domain.entities.document import Document
from modules.storage.infrastrucure.s3_service import S3Service

class DocumentSyncService:
    """
    Synchronise les documents d'un dossier avec les documents
    fournis par le formulaire.

    Le service crée les nouveaux documents, met à jour ceux dont
    le fichier a changé et supprime les documents qui ne sont
    plus présents dans les données reçues.
    
    Les fichiers associés sont également synchronisés avec
    le stockage S3.
    """

    def __init__(
        self,
        document_repository: DocumentRepository,
        s3_service: S3Service,
    ):
        self.document_repository = document_repository
        self.s3_service = s3_service

    """
    Synchronise les documents du dossier avec les données reçues.
    """

    def sync(
        self,
        application_id: str,
        documents: list[DocumentDTO],
    ):


        existing_docs = (
            self.document_repository
            .get_by_application(application_id)
        )


        existing_by_type = {
            doc.type: doc
            for doc in existing_docs
        }


        incoming_types = {
            doc.type
            for doc in documents
        }


        # =========================
        # UPSERT
        # =========================

        for incoming in documents:


            existing = existing_by_type.get(
                incoming.type
            )


            if existing:


                if existing.s3_key != incoming.s3_key:


                    self.s3_service.delete_file(
                        existing.s3_key
                    )


                    existing.s3_key = incoming.s3_key
                    existing.status = DocumentStatus.PENDING
                    existing.comment = None


                    self.document_repository.save(
                        existing
                    )


            else:


                self.document_repository.create(
                    Document(
                        id=str(uuid4()),
                        application_id=application_id,
                        type=incoming.type,
                        s3_key=incoming.s3_key,
                        status=DocumentStatus.PENDING,
                    )
                )


        # =========================
        # DELETE REMOVED
        # =========================

        for existing in existing_docs:


            if existing.type not in incoming_types:


                self.s3_service.delete_file(
                    existing.s3_key
                )


                self.document_repository.delete(
                    existing.id
                )