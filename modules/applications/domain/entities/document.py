from dataclasses import dataclass
from enum import Enum


class DocumentType(str, Enum):
    IDENTITY = "identity"
    RIB = "rib"
    PAYSLIP = "payslip"
    PROOF_OF_ADDRESS = "proof_of_address"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    REJECTED = "rejected"


@dataclass
class Document:
    id: str
    application_id: str

    type: DocumentType
    file_url: str

    status: DocumentStatus

    comment: str | None = None