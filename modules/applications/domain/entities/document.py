from dataclasses import dataclass
from modules.applications.domain.enums import DocumentStatus, DocumentType
from typing import Optional
from modules.applications.domain.entities.application import Application

@dataclass
class Document:
    id: str

    application_id: str

    type: DocumentType

    # clé S3 stockée en DB
    s3_key: str

    status: DocumentStatus

    comment: Optional[str] = None


    def update_status(
        self,
        status: DocumentStatus,
        comment: str | None = None
    ):

        self.status = status
        self.comment = comment