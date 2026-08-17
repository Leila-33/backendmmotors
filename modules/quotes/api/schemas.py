# modules/quotes/application/schemas.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from modules.applications.domain.enums import TradeInVehicleCondition
from modules.quotes.domain.enums import QuoteRefusalReason

# create quote
class QuoteTradeInRequest(BaseModel):

    brand: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    model: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    year: int = Field(
        ...,
        ge=1900
    )

    mileage: int = Field(
        ...,
        ge=0
    )

    condition: TradeInVehicleCondition



class CreateQuoteRequest(BaseModel):

    lead_id: str

    discount: float = 0

    down_payment: float = 0

    duration_months: int = 36

    trade_in: QuoteTradeInRequest | None = None

from pydantic import BaseModel


class CreateQuoteResponse(BaseModel):

    quote_id: str
    lead_id: str
    vehicle_id: str
    message: str


# get quote detail

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

    class Config:
        from_attributes = True

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
    

# get quotes

class CustomerQuoteListResponse(BaseModel):

    id: str

    status: str

    base_price: float

    monthly_payment: float

    vehicle: VehicleMiniResponse

    created_at: datetime

    requires_action: bool

    class Config:
        from_attributes = True


# get customer quote detail

class AgentMiniResponse(BaseModel):

    id: str

    first_name: str

    last_name: str


    class Config:
        from_attributes = True

class QuoteDetailCustomerResponse(BaseModel):

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


    class Config:
        from_attributes = True


# get client quote action required count



class QuoteActionRequiredCountResponse(
    BaseModel
):

    count: int


# accept/refuse quote




class RefuseQuoteRequest(BaseModel):

    reason: QuoteRefusalReason

    comment: str | None = None


class QuoteActionResponse(BaseModel):

    message: str

from pydantic import BaseModel


class AcceptQuoteResponse(BaseModel):
    quote_id: str

    message: str

    application_id: str


# update

class UpdateQuoteRequest(BaseModel):

    discount: float

    down_payment: float

    duration_months: int

    trade_in_value: float = 0

    trade_in: Optional[QuoteTradeInRequest] = None







class QuoteActionResponse(BaseModel):

    id: str

    message: str