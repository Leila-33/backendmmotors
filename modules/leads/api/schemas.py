from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# create lead
class CreateLeadRequest(BaseModel):
    vehicle_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    message: str




class CreateLeadResponse(BaseModel):
    lead_id: str
    status: str
    message: str




# get leads

class VehicleMiniResponse(BaseModel):
    id: str
    brand: str
    model: str
    price: float

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):

    id: str

    first_name: str
    last_name: str

    status: str
    vehicle : VehicleMiniResponse


    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# GET LEAD
# ==========================================

class AgentMiniResponse(BaseModel):
    id: str
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class QuoteMiniResponse(BaseModel):
    id: str
    status: str

    class Config:
        from_attributes = True


class LeadDetailResponse(BaseModel):
    id: str

    first_name: str
    last_name: str

    email: str
    phone: str
    message: str

    status: str

    vehicle: VehicleMiniResponse

    assigned_agent: Optional[AgentMiniResponse] = None

    quotes: list[QuoteMiniResponse] = []

    created_at: datetime

    can_create_quote : bool

    can_delete: bool

    class Config:
        from_attributes = True


# assign

class AssignLeadResponse(BaseModel):

    id: str
    status: str
    assigned_to: str

    message: str


# mark lead contacted
class MarkLeadContactedResponse(BaseModel):

    id: str

    status: str

    message: str


class QuoteLeadResponse(BaseModel):

    id: str

    first_name: str
    last_name: str

    email: str
    phone: str

    class Config:
        from_attributes = True