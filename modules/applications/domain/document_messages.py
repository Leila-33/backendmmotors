from modules.applications.domain.enums import DocumentStatus, EventType


DOCUMENT_LABELS = {
    "identity": {
        "label": "Pièce d'identité",
        "gender": "f"
    },
    "payslip": {
        "label": "Bulletin de salaire",
        "gender": "m"
    },
    "rib": {
        "label": "RIB",
        "gender": "m"
    },
    "address_proof": {
        "label": "Justificatif de domicile",
        "gender": "m"
    }
}

STATUS_MESSAGES = {
    DocumentStatus.VALIDATED: {
        "m": "a été validé",
        "f": "a été validée"
    },
    DocumentStatus.REJECTED: {
        "m": "a été refusé",
        "f": "a été refusée"
    },
}

DOCUMENT_EVENT_MAP = {
    DocumentStatus.VALIDATED: EventType.DOCUMENT_VALIDATED,
    DocumentStatus.REJECTED: EventType.DOCUMENT_REJECTED,
}