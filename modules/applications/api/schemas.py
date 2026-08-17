import re
from datetime import date, datetime
from typing import Any, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator,
    ValidationInfo
)

from modules.applications.domain.enums import EventType

from modules.applications.domain.enums import (
    ApplicationStatus,
    ApplicationType,
    DocumentStatus,
    DocumentType,
    TradeInVehicleCondition,
)

from modules.options.api.schemas import OptionResponse

from modules.payments.domain.enums import PaymentStatus

from modules.vehicles.domain.enums import (
    EngineType,
    VehicleType,
)
# ============================================================
# COMMON
# ============================================================

class ApplicationActionResponse(BaseModel):
    id: str
    status: ApplicationStatus
    message: str


# ============================================================
# CLIENT
# SAVE DRAFT APPLICATION
# ============================================================
class DocumentRequest(BaseModel):
    type: DocumentType
    s3_key: str


class TradeInRequest(BaseModel):
    enabled: bool = False

    brand: str | None = None
    model: str | None = None
    year: int | None = None
    mileage: int | None = None
    condition: TradeInVehicleCondition = (
        TradeInVehicleCondition.GOOD
    )

    @field_validator(
        "brand",
        "model",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None

        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v):

        if v is None:
            return v

        current_year = datetime.now().year
        if v < 1900:
            raise ValueError("Année invalide (min 1900)")

        if v > current_year:
            raise ValueError("Année ne peut pas être dans le futur")

        return v

    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):

        if v is None:
            return v

        if v < 0:
            raise ValueError("Kilométrage invalide")

        if v < 0:
            raise ValueError("Kilométrage doit être positif")
        
        if v > 1_000_000:
            raise ValueError("Kilométrage incohérent")

        return v

    @field_validator(
        "brand",
        "model",
        mode="before",
    )
    @classmethod
    def normalize_trade_in_text(cls, v):

        if v == "":
            return None

        if isinstance(v, str):
            v = v.strip()

        return v


class FinancingRequest(BaseModel):
    down_payment: float = Field(
        default=0,
        ge=0,
    )

    duration_months: int = Field(
        default=48,
        ge=1,
    )
    @field_validator("down_payment")
    @classmethod
    def validate_down_payment(cls, v):

        if v < 0:
            raise ValueError("Apport invalide")

        return v

    @field_validator("duration_months")
    @classmethod
    def validate_duration(cls, v):

        allowed = [24, 36, 48, 60]

        if v not in allowed:
            raise ValueError("Durée invalide")

        return v

class SelectedDatesRequest(BaseModel):
    start: date
    end: date
    @model_validator(mode="after")
    def validate_dates(self):

        if self.selected_dates is None:
            return self

        today = date.today()

        if self.selected_dates.start < today:
            raise ValueError(
                "La date de début doit être supérieure "
                "ou égale à aujourd'hui."
            )

        if self.selected_dates.end < self.selected_dates.start:
            raise ValueError(
                "La date de fin doit être après "
                "la date de début."
            )

        return self


class SaveDraftApplicationRequest(BaseModel):

    id: str | None = None

    vehicle_id: str | None = None

    application_type: ApplicationType | None = None

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: date | None = None

    selected_dates: SelectedDatesRequest | None = None

    monthly_income: float | None = Field(
        default=None,
        ge=0,
    )

    monthly_expenses: float | None = Field(
        default=None,
        ge=0,
    )

    employment_status: str | None = None

    selected_option_ids: list[str] = Field(
        default_factory=list
    )

    total_price: float | None = Field(
        default=None,
        gt=0,
    )

    financing: FinancingRequest | None = None

    trade_in: TradeInRequest | None = None

    documents: list[DocumentRequest] = Field(
        default_factory=list
    )

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "address",
        "employment_status",
        mode="before",
    )
    @classmethod
    def normalize_strings(cls, v):

        if isinstance(v, str):
            v = v.strip()
            return v or None

        return v

    # ========================================================
    # PHONE VALIDATION
    # ========================================================

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):

        if not v:
            return v

        phone_regex = r"^(0|\+33)[1-9](\d{8})$"

        if not re.match(phone_regex, v):
            raise ValueError("Téléphone invalide")

        return v

    # ========================================================
    # PRICE VALIDATION
    # ========================================================

    @field_validator("total_price")
    @classmethod
    def validate_price(cls, v):

        if v is None:
            return v

        if v <= 0:
            raise ValueError("Prix invalide")

        return v

    # ========================================================
    # FINANCIAL VALIDATION
    # ========================================================

    @field_validator(
        "monthly_income",
        "monthly_expenses",
    )
    @classmethod
    def validate_financials(cls, v):

        if v is None:
            return v

        if v < 0:
            raise ValueError(
                "Valeur financière invalide"
            )

        return v

    # ========================================================
    # DOCUMENTS VALIDATION
    # ========================================================

    @field_validator("documents")
    @classmethod
    def validate_documents(cls, v):

        if v is None:
            return []

        return v




# ============================================================
# SUBMIT APPLICATION
# ============================================================
class SubmitApplicationRequest(BaseModel):

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

    selected_dates: Optional[SelectedDatesRequest] = None

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

    financing: Optional[FinancingRequest] = None

    # =========================
    # TRADE-IN
    # =========================

    trade_in: Optional[TradeInRequest] = None

    # =========================
    # DOCUMENTS
    # =========================

    documents: list[DocumentRequest] = Field(
        default_factory=list
    )

    # =====================================================
    # REQUIRED STRINGS
    # =====================================================

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "address",
    )
    @classmethod
    def validate_required_strings(
        cls,
        value: str,
    ):
        value = value.strip()

        if not value:
            raise ValueError(
                "Champ obligatoire"
            )

        return value

    # =====================================================
    # PHONE
    # =====================================================

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):

        phone_regex = r"^(0|\+33)[1-9](\d{8})$"

        if not re.match(
            phone_regex,
            value,
        ):
            raise ValueError(
                "Téléphone invalide"
            )

        return value

    # =====================================================
    # TOTAL PRICE
    # =====================================================

    @field_validator("total_price")
    @classmethod
    def validate_total_price(
        cls,
        value: float,
    ):

        if value <= 0:
            raise ValueError(
                "Le prix total doit être supérieur à 0"
            )

        return value

    # =====================================================
    # BIRTH DATE
    # =====================================================

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(
        cls,
        value: date,
    ):

        today = date.today()

        age = (
            today.year
            - value.year
            - (
                (today.month, today.day)
                < (value.month, value.day)
            )
        )

        if age < 18:
            raise ValueError(
                "Le client doit être majeur"
            )

        return value

    # =====================================================
    # FINANCIAL VALUES
    # =====================================================

    @field_validator(
        "monthly_income",
        "monthly_expenses",
    )
    @classmethod
    def validate_financial_values(
        cls,
        value,
    ):

        if value is not None and value < 0:
            raise ValueError(
                "La valeur financière ne peut pas être négative"
            )

        return value

    # =====================================================
    # BUSINESS RULES
    # =====================================================

    @model_validator(mode="after")
    def validate_business_rules(self):

        # ---------------------------------
        # SALE
        # ---------------------------------

        if self.application_type == ApplicationType.SALE:

            if self.selected_dates is not None:
                raise ValueError(
                    "selected_dates non autorisé pour une vente"
                )

            if (
                self.monthly_income is None
                or self.monthly_income <= 0
            ):
                raise ValueError(
                    "Revenus requis pour un achat"
                )
            
            if self.monthly_expenses is None:
                raise ValueError(
                    "Dépenses requises pour un achat"
                )
            
            if not self.financing:
                raise ValueError(
                    "Financement requis pour un achat"
                )

            if not self.employment_status:
                raise ValueError(
                    "Situation professionnelle requise"
                )

        # ---------------------------------
        # RENT
        # ---------------------------------

        elif self.application_type == ApplicationType.RENT:

            if not self.selected_dates:
                raise ValueError(
                    "selected_dates requis pour une location"
                )

            if self.financing:
                raise ValueError(
                    "Pas de financement pour une location"
                )

            if self.trade_in:
                raise ValueError(
                    "Trade-in non autorisé pour une location"
                )

            if self.monthly_income or self.monthly_expenses:
                raise ValueError("Pas de données financières pour une location")

        return self

    # =====================================================
    # DOCUMENTS
    # =====================================================

    @model_validator(mode="after")
    def validate_required_documents(self):

        required_types = {
            "identity",
            "address_proof",
            "payslip",
            "rib",
        }

        received_types = {
            document.type
            for document in self.documents
        }

        missing = (
            required_types
            - received_types
        )

        if missing:
            raise ValueError(
                "Documents manquants : "
                + ", ".join(missing)
            )

        return self

# ============================================================
# GET APPLICATION
# ============================================================

class VehicleApplicationResponse(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    price: float
    type: VehicleType
    mileage: int
    engine_type: EngineType

    included_options: list[OptionResponse]
    optional_options: list[OptionResponse]


class FinancingResponse(BaseModel):
    down_payment: float
    duration_months: int
    financed_amount: float
    monthly_payment: float


class TradeInResponse(BaseModel):
    brand: str
    model: str
    year: int
    mileage: int
    condition: str
    estimated_value: float


class DocumentResponse(BaseModel):
    id: str
    application_id: str
    type: DocumentType
    s3_key: str
    status: DocumentStatus
    comment: str | None = None
    download_url: str


class EventResponse(BaseModel):
    id: str
    type: EventType
    message: str
    event_metadata: dict[str, Any] | None = None
    created_at: datetime


class ApplicationDetailResponse(BaseModel):

    # ========================================================
    # CORE
    # ========================================================

    id: str
    status: ApplicationStatus
    discount: float | None = None
    created_at: datetime

    # ========================================================
    # USER SNAPSHOT
    # ========================================================

    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None
    birth_date: date | None = None

    # ========================================================
    # FINANCIAL INFO
    # ========================================================

    monthly_income: float | None = None
    monthly_expenses: float | None = None
    employment_status: str | None = None

    # ========================================================
    # RENT
    # ========================================================

    selected_dates: SelectedDatesRequest | None = None

    # ========================================================
    # VEHICLE
    # ========================================================

    vehicle: VehicleApplicationResponse

    # ========================================================
    # OPTIONS
    # ========================================================

    options_selected: list[str]

    # ========================================================
    # FINANCING
    # ========================================================

    financing: FinancingResponse | None = None

    # ========================================================
    # TRADE-IN
    # ========================================================

    trade_in: TradeInResponse | None = None

    # ========================================================
    # DOCUMENTS
    # ========================================================

    documents: list[DocumentResponse]

    # ========================================================
    # EVENTS
    # ========================================================

    events: list[EventResponse]

    # ========================================================
    # PAYMENT
    # ========================================================

    payment_status: PaymentStatus | None = None


# ============================================================
# GET APPLICATIONS
# ============================================================

class ApplicationListBase(BaseModel):
    id: str
    type: ApplicationType
    vehicle: str
    status: ApplicationStatus
    submitted_at: datetime | None


class ApplicationListItemAdmin(ApplicationListBase):
    client: str

    can_cancel: bool
    can_restore_cancelled: bool = False
    can_archive: bool = False
    can_delete: bool = False


class ApplicationListItemUser(ApplicationListBase):
    created_at: datetime
    can_cancel: bool


class GetApplicationsResponse(BaseModel):
    items: list[
        ApplicationListItemAdmin |
        ApplicationListItemUser
    ]

    page: int
    limit: int
    total: int
    pages: int


# ============================================================
# GET APPLICATION BY VEHICLE
# ============================================================

class ApplicationByVehicleResponse(BaseModel):
    id: str
    status: ApplicationStatus


# ============================================================
# DELETE APPLICATION
# ============================================================

class DeleteApplicationResponse(BaseModel):
    id: str
    message: str


# ============================================================
# ADMIN
# UPDATE DOCUMENT
# ============================================================
class UpdateDocumentRequest(BaseModel):
    document_id: str
    status: DocumentStatus
    comment: str | None = None

class UpdateDocumentResponse(BaseModel):
    document_id: str
    status: DocumentStatus
    comment: str | None = None


# ============================================================
# GET APPLICATIONS
# ============================================================
class GetApplicationsRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: str | None = None
    status: str | None = None
    application_type: str | None = None
    sort: str = "created_at_desc"
    view_mode: str = "active"

# ============================================================
# GET EVENTS
# ============================================================

class EventDetailResponse(BaseModel):
    id: str
    type: str
    message: str
    event_metadata: dict[str, Any] | None = None

    created_at: datetime

    application_id: str | None = None
    test_drive_id: str | None = None
    user_id: str | None = None
    quote_id: str | None = None
    lead_id: str | None = None


class EventPaginationResponse(BaseModel):
    items: list[EventDetailResponse]

    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool
    has_previous: bool

# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

class UpdateApplicationStatusRequest(BaseModel):
    status: ApplicationStatus
    reason: Optional[str] = None
