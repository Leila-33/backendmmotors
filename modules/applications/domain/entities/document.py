from dataclasses import dataclass

from modules.applications.domain.enums import (
    DocumentStatus,
    DocumentType,
)


@dataclass
class Document:

    id: str

    application_id: str

    type: DocumentType

    # Clé S3 stockée en base de données
    s3_key: str

    status: DocumentStatus

    comment: str | None = None

    def update_status(
        self,
        status: DocumentStatus,
        comment: str | None = None,
    ) -> None:

        self.status = status
        self.comment = comment