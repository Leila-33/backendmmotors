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
    # =====================
    # IDENTIFIERS
    # =====================
    id: str
    user_id: str
    vehicle_id: str

    # =====================
    # USER SNAPSHOT
    # =====================
    first_name: str
    last_name: str
    email: str
    phone: str
    address: str
    birth_date: datetime

    # =====================
    # FINANCIAL INFO
    # =====================
    monthly_income: float
    monthly_expenses: float
    employment_status: str

    # =====================
    # OPTIONS (DOSSIER MÉTIER)
    # =====================
    options_included: List[str] = field(default_factory=list)
    options_optional: List[str] = field(default_factory=list)
    options_selected: List[str] = field(default_factory=list)

    # =====================
    # SYSTEM FIELDS
    # =====================
    created_at: datetime

    status: ApplicationStatus = ApplicationStatus.DRAFT
    document_ids: List[str] = field(default_factory=list)

    submitted_at: Optional[datetime] = None


