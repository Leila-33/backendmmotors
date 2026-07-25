from pydantic import BaseModel, ConfigDict
from datetime import datetime
from modules.sav.domain.enums import TicketPriority, TicketCategory, TicketStatus, TicketFilter
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict

# create support ticket

class SupportTicketCreate(BaseModel):
    subject: str
    category: TicketCategory
    priority: TicketPriority

    application_id: str | None = None

    message: str

class SupportTicketResponseDTO(BaseModel):
    id: str

    user_id: str
    application_id: Optional[str] = None

    subject: str
    category: TicketCategory
    priority: TicketPriority
    status: TicketStatus

    assigned_to: Optional[str] = None

    created_at: datetime
    updated_at: datetime

# get support ticket
class TicketMessageDTO(BaseModel):
    id: str
    sender_id: str
    sender_role: str
    message: str
    created_at: datetime


class SupportTicketResponseDTO(BaseModel):
    id: str
    user_id: str
    application_id: str | None

    subject: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority

    assigned_to: str | None

    created_at: datetime
    updated_at: datetime

    messages: list[TicketMessageDTO]


# find support tickets
class FindSupportTicketsQuery(BaseModel):
    page: int = 1
    limit: int = 10

    search: str = ""
    status: TicketStatus | Literal["ALL"] = "ALL"
    priority: TicketPriority | Literal["ALL"] = "ALL"
    category: TicketCategory | Literal["ALL"] = "ALL"

    sort: str = "created_at_desc"
    filter: TicketFilter = TicketFilter.ALL
    archive: bool = False
    
class SupportTicketItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # =====================
    # CORE TICKET FIELDS
    # =====================
    id: str
    subject: str
    category: str
    priority: str
    status: str

    user_id: str
    user_name: str | None = None

    assigned_to: str | None = None

    created_at: datetime
    updated_at: datetime

    # =====================
    # LAST ACTIVITY (UI LAYER ONLY)
    # =====================
    last_activity_at: datetime | None = None
    last_message_preview: str | None = None
    last_actor: str | None = None

    # =====================
    # UI STATE
    # =====================
    unread: bool = False

class PaginatedSupportTicketsResponse(BaseModel):
    items: list[SupportTicketItemDTO]

    page: int
    limit: int
    total: int
    pages: int


# update status
class UpdateTicketStatusDTO(BaseModel):
    status: TicketStatus



# Ticket message


class TicketMessageCreate(BaseModel):
    message: str


class TicketMessageResponse(BaseModel):
    id: str
    ticket_id: str
    sender_id: str
    sender_role: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}

class CountResponseDTO(BaseModel):
    count: int





# get support ticket
class TicketMessageDTO(BaseModel):
    id: str
    sender_id: str
    sender_role: str
    message: str
    created_at: datetime


class SupportTicketResponseDTO(BaseModel):
    id: str
    user_id: str
    application_id: str | None

    subject: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority

    assigned_to: str | None

    created_at: datetime
    updated_at: datetime

    messages: list[TicketMessageDTO]


# unread-count
class UnreadTicketCountResponse(BaseModel):
    count: int


# sav dashboard


class SavDashboardTicketDTO(BaseModel):
    id: str
    subject: str
    priority: str
    status: str
    created_at: datetime


class SavDashboardResponse(BaseModel):

    total: int
    open: int
    urgent: int

    recent_tickets: list[SavDashboardTicketDTO]


# sav statistics
class CategoryStat(BaseModel):
    category: str
    count: int


class SavStatisticsResponse(BaseModel):

    total: int
    closed: int

    last_7_days: int
    last_30_days: int

    category_distribution: list[CategoryStat]

    resolution_rate: float