from dataclasses import dataclass
from modules.applications.domain.enums import DocumentType

@dataclass
class DocumentDTO:
    type: DocumentType
    s3_key: str