from dataclasses import dataclass
from enum import Enum
from typing import List


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class Application:
    id: str

    user_id: str
    vehicle_id: str

    monthly_income: float
    monthly_expenses: float
    employment_status: str

    status: ApplicationStatus

    document_ids: List[str]