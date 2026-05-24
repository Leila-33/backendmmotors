from dataclasses import dataclass
from modules.core.enums import DocumentStatus, DocumentType
from typing import Optional

@dataclass
class Document:
    id: str

    application_id: str

    type: DocumentType

    # clé S3 stockée en DB
    s3_key: str

    status: DocumentStatus

    comment: Optional[str] = None