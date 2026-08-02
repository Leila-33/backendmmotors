from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from modules.applications.domain.enums import ApplicationStatus

from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing
)

from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn
)
from modules.financing.domain.entities.financing_contract import FinancingContract
from modules.vehicles.domain.entities.vehicle import Vehicle
from modules.reservations.domain.entities.reservation import Reservation
import uuid
from modules.auth.domain.entities.user import User


@dataclass
class Application:

    # =====================================================
    # IDENTIFIERS
    # =====================================================
    id: str

    user_id: str

    vehicle_id: str

    # =====================================================
    # OPTIONAL IDENTIFIERS
    # =====================================================
    quote_id: str | None = None


    # =====================================================
    # SNAPSHOT USER
    # =====================================================
    first_name: Optional[str] = None

    last_name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    address: Optional[str] = None

    birth_date: Optional[date] = None


    # =====================================================
    # FINANCIAL INFO
    # =====================================================
    monthly_income: Optional[float] = None

    monthly_expenses: Optional[float] = None

    employment_status: Optional[str] = None


    # =====================================================
    # STATUS
    # =====================================================
    status: ApplicationStatus = (
        ApplicationStatus.DRAFT
    )

    previous_status: Optional[ApplicationStatus] = None


    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    submitted_at: Optional[datetime] = None

    is_archived: bool = False

    deleted_at: Optional[datetime] = None

    discount: Optional[str] = None


    # =====================================================
    # RELATIONS OPTIONAL
    # =====================================================
    vehicle: Vehicle | None = None

    user: User | None = None

    financing_contract: FinancingContract | None = None

    reservation: Reservation | None = None

    option_ids: list[str] = field(
        default_factory=list
    )

    financing: ApplicationFinancing | None = None

    trade_in: ApplicationTradeIn | None = None

    documents: list = field(
        default_factory=list
    )

    options: list = field(
        default_factory=list
    )

    events: list = field(
        default_factory=list
    )

    notifications: list = field(
        default_factory=list
    )


    @staticmethod
    def create_draft_from_quote(
        quote,
        lead,
    ):
        return Application(
            id=str(uuid.uuid4()),

            quote_id=quote.id,

            user_id=lead.user_id,

            vehicle_id=lead.vehicle_id,

            first_name=lead.first_name,
            last_name=lead.last_name,
            email=lead.email,
            phone=lead.phone,

            status=ApplicationStatus.DRAFT,

            discount=quote.discount,
        )

    def change_status(
    self,
    status: ApplicationStatus
):
        self.previous_status = self.status
        self.status = status