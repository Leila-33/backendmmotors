from pydantic import BaseModel
from datetime import datetime

# =========================================================
# ADMIN - GET ANALYTICS
# =========================================================
class ApplicationByDayResponse(BaseModel):
    date: str
    count: int


class StatusDistributionResponse(BaseModel):
    name: str
    value: int


class RevenueByMonthResponse(BaseModel):
    month: str
    amount: float


class AnalyticsStatsResponse(BaseModel):
    total: int
    approved: int
    rejected: int
    submitted: int
    draft: int


class AnalyticsResponse(BaseModel):
    applications_by_day: list[
        ApplicationByDayResponse
    ]

    status_distribution: list[
        StatusDistributionResponse
    ]

    revenue: list[
        RevenueByMonthResponse
    ]

    stats: AnalyticsStatsResponse


# =========================================================
# ADMIN - GET DASHBOARD
# =========================================================

class DashboardStatsResponse(BaseModel):
    total_applications: int
    pending_applications: int
    active_applications: int
    rejected_applications: int
    archived_applications: int
    applications_this_week: int


class RecentApplicationResponse(BaseModel):
    id: str
    status: str
    first_name: str
    last_name: str
    created_at: datetime


class RecentEventResponse(BaseModel):
    id: str
    type: str
    message: str
    created_at: datetime


class AdminDashboardResponse(BaseModel):
    stats: DashboardStatsResponse
    recent_applications: list[RecentApplicationResponse]
    recent_events: list[RecentEventResponse]



# =========================================================
# USER - GET DASHBOARD
# =========================================================


class DashboardApplicationResponse(BaseModel):

    id: str
    status: str
    created_at: datetime


class DashboardVehicleResponse(BaseModel):
    id: str
    brand: str
    model: str

class DashboardTestDriveResponse(BaseModel):
    id: str
    appointment_date: datetime
    status: str
    vehicle: DashboardVehicleResponse
    
class DashboardNotificationResponse(BaseModel):

    id: str
    title: str
    message: str
    status: str
    created_at: datetime


class DashboardResponse(BaseModel):
    total_applications: int
    active_applications: int
    approved_applications: int
    pending_applications: int

    applications: list[
        DashboardApplicationResponse
    ]

    upcoming_test_drive: (
        DashboardTestDriveResponse | None
    )

    unread_notifications: int

    notifications: list[
        DashboardNotificationResponse
    ]
