from dataclasses import dataclass

from modules.applications.domain.enums import DocumentStatus


@dataclass
class UpdateDocumentResult:
    document_id: str
    status: DocumentStatus
    comment: str | None