from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from datetime import datetime


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

    # 🔹 champs obligatoires d'abord
    created_at: datetime

    # 🔹 ensuite les champs avec défaut
    status: ApplicationStatus = ApplicationStatus.DRAFT
    document_ids: List[str] = field(default_factory=list)

    submitted_at: Optional[datetime] = None


