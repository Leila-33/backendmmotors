from dataclasses import dataclass
from datetime import datetime


@dataclass
class DashboardApplicationItemResult:
    id: str
    status: str
    created_at: datetime

@dataclass
class DashboardVehicleResult:
    id: str
    brand: str
    model: str


@dataclass
class DashboardTestDriveResult:
    id: str
    appointment_date: datetime
    status: str
    vehicle: DashboardVehicleResult

@dataclass
class DashboardNotificationItemResult:
    id: str
    title: str
    message: str
    status: str
    created_at: datetime


@dataclass
class DashboardResult:
    total_applications: int
    active_applications: int
    approved_applications: int
    pending_applications: int

    applications: list[
        DashboardApplicationItemResult
    ]

    upcoming_test_drive: (
        DashboardTestDriveResult | None
    )

    unread_notifications: int

    notifications: list[
        DashboardNotificationItemResult
    ]