import uuid

from dataclasses import dataclass, field
from datetime import date, datetime, timezone

from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing,
)
from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn,
)
from modules.applications.domain.enums import ApplicationStatus

from modules.auth.domain.entities.user import User

from modules.financing.domain.entities.financing_contract import (
    FinancingContract,
)

from modules.reservations.domain.entities.reservation import (
    Reservation,
)

from modules.vehicles.domain.entities.vehicle import Vehicle


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
    # USER SNAPSHOT
    # =====================================================

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: date | None = None

    # =====================================================
    # FINANCIAL INFO
    # =====================================================

    monthly_income: float | None = None
    monthly_expenses: float | None = None
    employment_status: str | None = None

    # =====================================================
    # STATUS
    # =====================================================

    status: ApplicationStatus = ApplicationStatus.DRAFT

    previous_status: ApplicationStatus | None = None

    # =====================================================
    # DATES
    # =====================================================

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    submitted_at: datetime | None = None

    # =====================================================
    # ARCHIVE / DELETE
    # =====================================================

    is_archived: bool = False

    deleted_at: datetime | None = None

    # =====================================================
    # PRICING SNAPSHOT
    # =====================================================

    # Prix du véhicule au moment du dossier.
    base_price: float | None = None

    # Total des options sélectionnées.
    optional_price: float | None = None

    # Remise appliquée au dossier.
    discount: float | None = None

    # Prix total retenu pour le dossier.
    total_price: float | None = None


    # =====================================================
    # RELATIONS
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

    # =====================================================
    # FACTORY
    # =====================================================

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
            total_price=quote.base_price,

            discount=quote.discount,
        )

    # =====================================================
    # STATUS
    # =====================================================

    def change_status(
        self,
        status: ApplicationStatus,
    ):

        self.previous_status = self.status
        self.status = status