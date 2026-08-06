from pydantic import BaseModel, HttpUrl, field_validator, model_validator, Field, EmailStr
from typing import List, Optional
from modules.applications.domain.enums import DocumentType, DocumentStatus, ViewMode
from datetime import datetime, date
import re
from modules.applications.domain.enums import (
    TradeInVehicleCondition,
    ApplicationStatus
)
from typing import List
from datetime import datetime
from modules.applications.domain.enums import ApplicationStatus, ApplicationType
# =========================
# save draft application
# =========================

from modules.applications.domain.entities.application import Application

class ApplicationFormResult(BaseModel):
    application: Application
    is_new: bool

class DocumentDTO(BaseModel):

    type: str
    s3_key: str


class TradeInDTO(BaseModel):

    enabled: bool = False

    brand: Optional[str] = None
    model: Optional[str] = None

    year: Optional[int] = None
    mileage: Optional[int] = None

    condition: Optional[TradeInVehicleCondition] = (
        TradeInVehicleCondition.GOOD
    )

    @field_validator(
        "brand",
        "model",
        mode="before"
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

        if v < 1980 or v > current_year:
            raise ValueError("Année invalide")

        return v

    @field_validator("mileage")
    @classmethod
    def validate_mileage(cls, v):

        if v is None:
            return v

        if v < 0:
            raise ValueError("Kilométrage invalide")

        return v

    @field_validator("brand", "model")
    @classmethod
    def validate_text(cls, v):

        if v is None:
            return v

        value = v.strip()

        if not value:
            raise ValueError("Champ requis")

        return value



class FinancingDTO(BaseModel):

    down_payment: float = 0

    duration_months: int = 48

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


class SelectedDatesDTO(BaseModel):

    start: date
    end: date
    @model_validator(mode="after")
    def validate_dates(self):

        today = date.today()

        if self.start < today:
            raise ValueError(
                "La date de début doit être supérieure ou égale à aujourd'hui."
            )

        if self.end < self.start:
            raise ValueError(
                "La date de fin doit être après la date de début."
            )

        return self

class SaveDraftApplicationDTO(BaseModel):

    # =========================
    # IDS
    # =========================
    id: Optional[str] = None
    vehicle_id: Optional[str] = None

    # =========================
    # TYPE
    # =========================
    application_type: Optional[ApplicationType] = None  # "sale" | "rent"

    # =========================
    # USER INFOS
    # =========================
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None

    # =========================
    # RENT ONLY
    # =========================
    selected_dates: Optional[SelectedDatesDTO] = None

    # =========================
    # FINANCIAL (SALE ONLY)
    # =========================
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None

    # =========================
    # OPTIONS
    # =========================
    selected_option_ids: list[str] = Field(default_factory=list)

    # =========================
    # PRICE
    # =========================
    total_price: Optional[float] = None

    # =========================
    # FINANCING (SALE ONLY)
    # =========================
    financing: Optional[FinancingDTO] = None

    # =========================
    # TRADE-IN (SALE ONLY)
    # =========================
    trade_in: Optional[TradeInDTO] = None

    # =========================
    # DOCUMENTS
    # =========================
    documents: list[DocumentDTO] = Field(default_factory=list)

    # =====================================================
    # NORMALIZATION
    # =====================================================
    @field_validator(
        "first_name",
        "last_name",
        "email",
        "phone",
        "address",
        "birth_date",
        "employment_status",
        mode="before"
    )
    @classmethod
    def normalize_strings(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


    # =====================================================
    # PHONE VALIDATION (FR simple)
    # =====================================================
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v:
            return v

        phone_regex = r"^(0|\+33)[1-9](\d{8})$"
        if not re.match(phone_regex, v):
            raise ValueError("Téléphone invalide")

        return v

    # =====================================================
    # PRICE VALIDATION
    # =====================================================
    @field_validator("total_price")
    @classmethod
    def validate_price(cls, v):
        if v is None:
            return v

        if v <= 0:
            raise ValueError("Prix invalide")

        return v

    # =====================================================
    # FINANCIAL VALIDATION
    # =====================================================
    @field_validator("monthly_income", "monthly_expenses")
    @classmethod
    def validate_financials(cls, v):
        if v is None:
            return v

        if v < 0:
            raise ValueError("Valeur financière invalide")

        return v

    # =====================================================
    # DOCUMENTS BASIC VALIDATION
    # =====================================================
    @field_validator("documents")
    @classmethod
    def validate_documents(cls, v):
        if v is None:
            return []

        return v
    
    @model_validator(mode="after")
    def validate_income_vs_expenses(self):

        if (
            self.monthly_income is not None
            and self.monthly_expenses is not None
        ):

            if self.monthly_expenses > self.monthly_income:
                raise ValueError(
                    "Les charges mensuelles ne peuvent pas dépasser les revenus"
                )

        return self


class SaveDraftApplicationResponse(BaseModel):
    id: str
    status: ApplicationStatus





# =========================
# submit application
# =========================
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
    selected_dates: Optional[SelectedDatesDTO] = None
    # =========================
    # TYPE
    # =========================
    application_type: ApplicationType

    # =========================
    # FINANCIAL (SALE ONLY)
    # =========================
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None

    # =========================
    # OPTIONS
    # =========================
    selected_option_ids: list[str] = Field(default_factory=list)

    # =========================
    # PRICE
    # =========================
    total_price: float

    # =========================
    # FINANCING (SALE ONLY)
    # =========================
    financing: Optional[FinancingDTO] = None

    # =========================
    # TRADE-IN (SALE ONLY)
    # =========================
    trade_in: Optional[TradeInDTO] = None

    # =========================
    # DOCUMENTS
    # =========================
    documents: list[DocumentDTO] = Field(default_factory=list)
    # =====================================================
    # STRING VALIDATION
    # =====================================================

    @field_validator(
        "first_name",
        "last_name",
        "phone",
        "address",
    )
    @classmethod
    def validate_required_strings(cls, value: str):

        if not value or not value.strip():
            raise ValueError("Champ obligatoire")

        return value.strip()

    
    @model_validator(mode="after")
    def validate_business_rules(self):
        if self.application_type == ApplicationType.SALE:

            if self.selected_dates is not None:
                raise ValueError(
                    "selected_dates non autorisé pour une vente"
                )

            if not self.monthly_income or self.monthly_income <= 0:
                raise ValueError("Revenus requis pour un achat")

            if self.monthly_expenses is not None and self.monthly_expenses < 0:
                raise ValueError("Les charges ne peuvent pas être négatives")
            
            if self.monthly_expenses >= self.monthly_income:
                raise ValueError(
                    "Les charges doivent être inférieures aux revenus"
                )

            if not self.financing:
                raise ValueError("Financement requis pour un achat")

            if not self.employment_status:
                raise ValueError("Situation professionnelle requise")

        elif self.application_type == ApplicationType.RENT:
            if not self.selected_dates:
                raise ValueError(
                    "selected_dates requis pour une location"
                )

            if self.selected_dates.start > self.selected_dates.end:
                raise ValueError(
                    "Date de début invalide"
                )
            if self.selected_dates.start < date.today():
                raise ValueError("Date de début passée invalide")
            
            if self.financing:
                raise ValueError("Pas de financement pour une location")

            if self.monthly_income or self.monthly_expenses:
                raise ValueError("Pas de données financières pour une location")

            if self.trade_in:
                raise ValueError("Trade-in non autorisé pour une location")
        return self




    # =====================================================
    # TOTAL PRICE
    # =====================================================

    @field_validator("total_price")
    @classmethod
    def validate_total_price(cls, value: float):

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
    def validate_birth_date(cls, value: date):

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
    # REQUIRED DOCUMENTS VALIDATION
    # =====================================================

    @model_validator(mode="after")
    def validate_required_documents(self):

        required_types = {
            "identity",
            "address_proof",
            "payslip",
            "rib"
        }

        received_types = {
            doc.type for doc in self.documents
        }

        missing = required_types - received_types

        if missing:

            raise ValueError(
                f"Documents manquants : {', '.join(missing)}"
            )

        return self
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if not v:
            return v

        phone_regex = r"^(0|\+33)[1-9](\d{8})$"
        if not re.match(phone_regex, v):
            raise ValueError("Téléphone invalide")

        return v



# =========================
# get application
# =========================
from modules.vehicles.domain.enums import (
    VehicleType,
    EngineType
)
from modules.options.api.schemas import OptionResponse
from modules.applications.domain.enums import ApplicationStatus
from modules.payments.domain.enums import PaymentStatus
from modules.applications.domain.entities.event import EventType
from typing import Any

class VehicleApplicationResponse(BaseModel):

    id: str

    brand: str

    model: str

    year: int

    price: float

    type: VehicleType

    mileage: int

    engine_type: EngineType

    included_options: list["OptionResponse"]

    optional_options: list["OptionResponse"]



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

    # =========================
    # CORE
    # =========================
    id: str

    status: ApplicationStatus

    discount: float | None = None

    created_at: datetime

    # =========================
    # USER SNAPSHOT
    # =========================
    first_name: str | None = None

    last_name: str | None = None

    email: str | None = None

    phone: str | None = None

    address: str | None = None

    birth_date: date | None = None

    # =========================
    # FINANCIAL INFO
    # =========================
    monthly_income: float | None = None

    monthly_expenses: float | None = None

    employment_status: str | None = None

    # =========================
    # RENT
    # =========================
    selected_dates: SelectedDatesDTO | None = None

    # =========================
    # VEHICLE
    # =========================
    vehicle: VehicleApplicationResponse

    # =========================
    # OPTIONS
    # =========================
    options_selected: list[str]

    # =========================
    # FINANCING
    # =========================
    financing: FinancingResponse | None = None

    # =========================
    # TRADE-IN
    # =========================
    trade_in: TradeInResponse | None = None

    # =========================
    # DOCUMENTS
    # =========================
    documents: list[DocumentResponse]

    # =========================
    # EVENTS
    # =========================
    events: list[EventResponse]

    # =========================
    # PAYMENT
    # =========================
    payment_status: PaymentStatus | None = None








# =========================
# get_applications
# =========================

class GetApplicationsDTO(BaseModel):

    page: int
    limit: int

    search: str | None = None
    status: str | None = None
    application_type: str | None = None

    sort: str = "created_at_desc"

    view_mode: ViewMode = ViewMode.ACTIVE


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



# =========================
# get application by vehicle
# =========================
class ApplicationByVehicleResponse(BaseModel):

    id: str
    status: ApplicationStatus





# =========================
# delete application
# =========================
class DeleteApplicationResponseDTO(BaseModel):
    success: bool
    application_id: str












# ADMIN


# archive

class ApplicationActionResponse(BaseModel):

    id: str

    status: ApplicationStatus

    message: str









# =========================
# upload_document
# =========================
class CreateApplicationOnboardingRequest(BaseModel):

    # =========================
    # CONTEXTE
    # =========================
    application_id: Optional[str] = None
    vehicle_id: Optional[str] = None

    # =========================
    # APPLICATION DATA (optionnel car mode creation)
    # =========================
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None

    # =========================
    # DOCUMENT
    # =========================
    type: DocumentType
    file_url: HttpUrl

    # =========================
    # VALIDATION MÉTIER
    # =========================
    @model_validator(mode="after")
    def check_consistency(self):

        # mode creation
        if not self.application_id:
            if not self.vehicle_id:
                raise ValueError("vehicle_id required if creating application")

        return self

    # =========================
    # VALIDATION FICHIER (option fragile)
    # =========================
    @field_validator("file_url")
    @classmethod
    def validate_extension(cls, v: HttpUrl):

        url = str(v).lower()

        if not url.endswith((".pdf", ".jpg", ".jpeg", ".png")):
            raise ValueError("Format autorisé : PDF, JPG, PNG")

        return v

class DocumentResponsel(BaseModel):
    id: str
    type: str
    status: str



# =========================
# submit_application
# =========================
class SubmitApplicationResponse(BaseModel):
    id: str
    status: str
    message: str


# =========================
# update_application
# =========================
class UpdateApplicationFullRequest(BaseModel):
    monthly_income: Optional[float] = None
    monthly_expenses: Optional[float] = None
    employment_status: Optional[str] = None
    selected_options: Optional[List[str]] = None

    @field_validator("selected_options")
    @classmethod
    def validate_options(cls, v):
        if v is not None and len(v) == 0:
            raise ValueError("selected_options cannot be empty list")
        return v

    @field_validator("monthly_income")
    @classmethod
    def validate_income(cls, v):
        if v is not None and v < 0:
            raise ValueError("monthly_income must be >= 0")
        return v

    @field_validator("monthly_expenses")
    @classmethod
    def validate_expenses(cls, v):
        if v is not None and v < 0:
            raise ValueError("monthly_expenses must be >= 0")
        return v


class UpdateApplicationResponse(BaseModel):
    id: str
    status: str
    selected_options: List[str]
    message: str


# =========================
# list_applications
# =========================
# =========================================
# app/application/dto/get_applications_dto.py
# =========================================








# =========================
# get_application_detail
# =========================


class DocumentDTO(BaseModel):
    id: str
    type: str
    file_url: str
    status: str
    comment: Optional[str]


class EventDTO(BaseModel):
    type: str
    message: str
    date: str
    user_id: Optional[str]

# update document



class UpdateDocumentDTO(BaseModel):

    document_id: str

    status: DocumentStatus

    comment: str | None = None




class UpdateDocumentResponseDTO(BaseModel):

    document_id: str

    status: DocumentStatus

    comment: Optional[str] = None
    
# =========================
# approve_application reject_application
# =========================

from modules.applications.domain.enums import ApplicationStatus


class UpdateApplicationStatusDTO(BaseModel):
    status: ApplicationStatus
    reason: Optional[str] = None



class UpdateApplicationStatusResponseDTO(BaseModel):
    application_id: str
    status: ApplicationStatus
    message: str




class SubmitApplicationResponse(BaseModel):
    id: str
    status: ApplicationStatus
    message: str




class ApplicationCancelResponse(BaseModel):
    id: str
    status: str
    message: str

from pydantic import BaseModel


class ApplicationRestoreCancelledResponse(BaseModel):
    id: str
    status: str
    message: str


class TradeInSnapshot(BaseModel):

    brand: str

    model: str

    year: int

    mileage: int

    condition: str






# =========================
# get_events
# =========================
class EventDetailResponse(BaseModel):

    id: str
    type: str
    message: str
    event_metadata: dict | None = None

    created_at: datetime

    application_id: str | None = None
    test_drive_id: str | None = None
    user_id: str | None = None


class EventPaginationResponse(BaseModel):

    items: list[EventDetailResponse]

    total: int

    page: int

    limit: int

    total_pages: int

    has_next: bool

    has_previous: bool