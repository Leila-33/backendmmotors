from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from modules.auth.domain.enums import UserRole
from modules.sav.domain.enums import (
    TicketCategory,
    TicketFilter,
    TicketPriority,
    TicketStatus,
)


# =========================================================
# CLIENT
# =========================================================


# =========================================================
# CREATE SUPPORT TICKET
# =========================================================

class CreateSupportTicketRequest(BaseModel):

    subject: str

    category: TicketCategory

    priority: TicketPriority

    application_id: str | None = None

    message: str


# =========================================================
# GET SUPPORT TICKET
# =========================================================

class TicketMessageResponse(BaseModel):

    id: str

    sender_id: str

    sender_role: UserRole

    message: str

    created_at: datetime


class SupportTicketResponse(BaseModel):

    id: str

    user_id: str

    application_id: str | None

    subject: str

    description: str

    category: TicketCategory

    status: TicketStatus

    priority: TicketPriority

    assigned_to: str | None

    created_at: datetime

    updated_at: datetime | None = None

    archived_at: datetime | None = None

    messages: list[TicketMessageResponse]


# =========================================================
# FIND SUPPORT TICKETS
# =========================================================

class FindSupportTicketsQuery(BaseModel):

    page: int = 1

    limit: int = 10

    search: str = ""

    status: (
        TicketStatus
        | Literal["ALL"]
    ) = "ALL"

    priority: (
        TicketPriority
        | Literal["ALL"]
    ) = "ALL"

    category: (
        TicketCategory
        | Literal["ALL"]
    ) = "ALL"

    sort: str = "created_at_desc"

    filter: TicketFilter = TicketFilter.ALL

    archive: bool = False


class SupportTicketListItemResponse(BaseModel):

    # =====================================================
    # TICKET
    # =====================================================

    id: str

    subject: str

    category: TicketCategory

    status: TicketStatus

    priority: TicketPriority

    # =====================================================
    # CLIENT
    # =====================================================

    user_id: str

    user_name: str | None = None

    # =====================================================
    # LAST ACTIVITY
    # =====================================================

    last_message_preview: str | None = None

    last_actor: str | None = None

    last_activity_at: datetime | None = None

    # =====================================================
    # READ STATE
    # =====================================================

    unread: bool = False

    # =====================================================
    # DATES
    # =====================================================

    created_at: datetime

    updated_at: datetime | None = None

    archived_at: datetime | None = None


# =========================================================
# TICKET CHAT
# =========================================================

class TicketMessageCreate(BaseModel):

    message: str


# =========================================================
# AGENT
# =========================================================


# =========================================================
# UPDATE STATUS
# =========================================================

class UpdateSupportTicketStatusRequest(BaseModel):

    status: TicketStatus


# =========================================================
# UNREAD COUNT
# =========================================================

class UnreadTicketCountResponse(BaseModel):

    count: int


# =========================================================
# SAV DASHBOARD
# =========================================================

class SavDashboardTicketResponse(BaseModel):

    id: str

    subject: str

    priority: TicketPriority

    status: TicketStatus

    created_at: datetime


class SavDashboardResponse(BaseModel):

    total: int

    open: int

    urgent: int

    recent_tickets: list[
        SavDashboardTicketResponse
    ]


# =========================================================
# SAV STATISTICS
# =========================================================

class CategoryStat(BaseModel):

    category: TicketCategory

    count: int


class SavStatisticsResponse(BaseModel):

    total: int

    closed: int

    last_7_days: int

    last_30_days: int

    category_distribution: list[
        CategoryStat
    ]

    resolution_rate: float