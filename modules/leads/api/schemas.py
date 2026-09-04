from pydantic import BaseModel
from datetime import datetime
from typing import Optional
# ==========================================
# CLIENT
# ==========================================

# ==========================================
# CREATE LEAD
# ==========================================
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


# ==========================================
# ADMIN
# ==========================================

# ==========================================
# GET SALES LEADS
# ==========================================

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

class GetSalesLeadsResponse(BaseModel):
    items: list[LeadListResponse]
# ==========================================
# GET LEAD DETAIL
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


# ==========================================
# ASSIGN LEAD
# ==========================================

class AssignLeadResponse(BaseModel):

    id: str
    status: str
    assigned_to: str

    message: str


# ==========================================
# MARK LEAD AS CONTACTED
# ==========================================
class MarkLeadContactedResponse(BaseModel):

    id: str

    status: str

    message: str

# ==========================================
# DELETE LEAD
# ==========================================
class DeleteLeadResponse(BaseModel):
    id: str
    message: str




# ==========================================
# SALES DASHBOARD STATISTICS
# ==========================================
class SalesDashboardStatisticsResponse(BaseModel):
    new_leads: int
    my_leads: int
    quotes_sent: int
    applications: int
    unassigned: int
    won: int
    lost: int
    conversion_rate: float


# ==========================================
# SALES NOTIFICATION COUNTS
# ==========================================
class SalesNotificationCountsResponse(BaseModel):
    new_leads_count: int
    my_leads_count: int