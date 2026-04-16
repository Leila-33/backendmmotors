from dataclasses import dataclass, field
from typing import List
from enum import Enum


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

    status: ApplicationStatus = ApplicationStatus.DRAFT

    document_ids: List[str] = field(default_factory=list)