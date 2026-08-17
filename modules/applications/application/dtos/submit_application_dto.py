from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

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


class SubmitApplicationDTO(BaseModel):

    # =========================
    # IDS
    # =========================

    id: Optional[str] = None
    vehicle_id: str

    # =========================
    # USER INFOS
    # =========================

    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    address: str
    birth_date: date

    # =========================
    # TYPE
    # =========================

    application_type: ApplicationType

    # =========================
    # RENT
    # =========================

    selected_dates: Optional[SelectedDatesDTO] = None

    # =========================
    # FINANCIAL
    # =========================

    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None

    # =========================
    # OPTIONS
    # =========================

    selected_option_ids: list[str] = Field(
        default_factory=list
    )

    # =========================
    # PRICE
    # =========================

    total_price: float

    # =========================
    # FINANCING
    # =========================

    financing: Optional[FinancingDTO] = None

    # =========================
    # TRADE-IN
    # =========================

    trade_in: Optional[TradeInDTO] = None

    # =========================
    # DOCUMENTS
    # =========================

    documents: list[DocumentDTO] = Field(
        default_factory=list
    )