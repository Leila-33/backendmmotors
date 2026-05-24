# =========================================================
# DOMAIN ENTITY
# modules/applications/domain/entities/application.py
# =========================================================

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from modules.core.enums import (
    ApplicationStatus
)

from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing
)

from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn
)


@dataclass
class Application:

    # =====================================================
    # IDENTIFIERS
    # =====================================================
    id: str

    user_id: str

    vehicle_id: str

    # =====================================================
    # SNAPSHOT USER
    # DRAFT => optional
    # SUBMIT => validated later
    # =====================================================
    first_name: Optional[str] = None

    last_name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    address: Optional[str] = None

    birth_date: Optional[datetime] = None

    # =====================================================
    # FINANCIAL INFO
    # =====================================================
    monthly_income: Optional[float] = None

    monthly_expenses: Optional[float] = None

    employment_status: Optional[str] = None

    # =====================================================
    # STATUS
    # =====================================================
    status: ApplicationStatus = ApplicationStatus.DRAFT

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    submitted_at: Optional[datetime] = None

    is_archived: bool = False
    
    deleted_at: Optional[datetime] = None

    # =====================================================
    # RELATIONS
    # =====================================================
    financing: Optional[ApplicationFinancing] = None

    trade_in: Optional[ApplicationTradeIn] = None

    documents: list = field(default_factory=list)

    options: list = field(default_factory=list)

    events: list = field(default_factory=list)

    notifications: list = field(default_factory=list)