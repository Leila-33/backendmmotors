from dataclasses import dataclass
from datetime import date
from modules.applications.domain.enums import ApplicationType

from modules.applications.application.dtos.financing_dto import (
    FinancingDTO,
)
from modules.applications.application.dtos.trade_in_dto import (
    TradeInDTO,
)
from modules.applications.application.dtos.document_dto import (
    DocumentDTO,
)
from modules.applications.application.dtos.selected_dates_dto import (
    SelectedDatesDTO,
)

@dataclass
class SaveDraftApplicationDTO:

    id: str | None
    vehicle_id: str | None

    application_type: ApplicationType | None

    first_name: str | None
    last_name: str | None
    email: str | None
    phone: str | None
    address: str | None
    birth_date: date | None

    selected_dates: SelectedDatesDTO | None

    monthly_income: float | None
    monthly_expenses: float | None
    employment_status: str | None

    selected_option_ids: list[str]

    total_price: float | None

    financing: FinancingDTO | None

    trade_in: TradeInDTO | None

    documents: list[DocumentDTO]