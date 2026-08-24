# modules/quotes/api/schemas.py

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from modules.applications.domain.enums import (
    TradeInVehicleCondition,
)
from modules.quotes.domain.enums import (
    QuoteRefusalReason,
)


# =========================================================
# COMMON
# =========================================================

class QuoteActionResponse(BaseModel):
    id: str
    message: str


# =========================================================
# AGENT - CREATE QUOTE
# =========================================================

class QuoteTradeInRequest(BaseModel):

    brand: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    model: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    year: int = Field(
        ...,
        ge=1900,
    )

    mileage: int = Field(
        ...,
        ge=0,
    )

    condition: TradeInVehicleCondition


class CreateQuoteRequest(BaseModel):

    lead_id: str

    discount: float = Field(
        default=0,
        ge=0,
    )

    down_payment: float = Field(
        default=0,
        ge=0,
    )

    duration_months: int = Field(
        default=36,
        gt=0,
    )

    trade_in: QuoteTradeInRequest | None = None


class CreateQuoteResponse(BaseModel):

    quote_id: str

    lead_id: str

    vehicle_id: str

    message: str


# =========================================================
# AGENT - GET QUOTE DETAIL
# =========================================================

class QuoteTradeInResponse(BaseModel):

    brand: str

    model: str

    year: int

    mileage: int

    condition: str

    estimated_value: float


class QuoteLeadResponse(BaseModel):

    id: str

    first_name: str

    last_name: str

    email: str

    phone: str

    model_config = ConfigDict(
        from_attributes=True
    )


class VehicleMiniResponse(BaseModel):

    id: str

    brand: str

    model: str

    price: float

    model_config = ConfigDict(
        from_attributes=True
    )


class QuoteDetailResponse(BaseModel):

    id: str

    status: str

    base_price: float

    discount: float

    down_payment: float

    trade_in_value: float

    financed_amount: float

    duration_months: int

    monthly_payment: float

    lead: QuoteLeadResponse

    vehicle: VehicleMiniResponse

    trade_in: QuoteTradeInResponse | None = None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# AGENT - UPDATE QUOTE
# =========================================================

class UpdateQuoteRequest(BaseModel):

    discount: float = Field(
        ...,
        ge=0,
    )

    down_payment: float = Field(
        ...,
        ge=0,
    )

    duration_months: int = Field(
        ...,
        gt=0,
    )

    trade_in: QuoteTradeInRequest | None = None


# =========================================================
# CUSTOMER - GET QUOTES
# =========================================================

class CustomerQuoteListResponse(BaseModel):

    id: str

    status: str

    base_price: float

    monthly_payment: float

    vehicle: VehicleMiniResponse

    created_at: datetime

    requires_action: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# CUSTOMER - GET QUOTE DETAIL
# =========================================================

class AgentMiniResponse(BaseModel):

    id: str

    first_name: str

    last_name: str

    model_config = ConfigDict(
        from_attributes=True
    )


class QuoteCustomerDetailResponse(BaseModel):

    id: str

    status: str

    base_price: float

    discount: float

    down_payment: float

    trade_in_value: float

    financed_amount: float

    duration_months: int

    monthly_payment: float

    vehicle: VehicleMiniResponse

    trade_in: QuoteTradeInResponse | None = None

    sales_agent: AgentMiniResponse | None = None

    created_at: datetime

    application_id: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# CUSTOMER - ACTION REQUIRED COUNT
# =========================================================

class QuoteActionRequiredCountResponse(BaseModel):

    count: int


# =========================================================
# CUSTOMER - ACCEPT QUOTE
# =========================================================

class AcceptQuoteResponse(BaseModel):

    quote_id: str

    application_id: str

    message: str


# =========================================================
# CUSTOMER - REFUSE QUOTE
# =========================================================

class RefuseQuoteRequest(BaseModel):

    reason: QuoteRefusalReason

    comment: str | None = None




