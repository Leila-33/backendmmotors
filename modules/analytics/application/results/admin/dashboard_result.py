from dataclasses import dataclass
from datetime import datetime


@dataclass
class DashboardStatsResult:
    total_applications: int
    pending_applications: int
    active_applications: int
    rejected_applications: int
    archived_applications: int
    applications_this_week: int


@dataclass
class RecentApplicationResult:
    id: str
    status: str
    first_name: str
    last_name: str
    created_at: datetime


@dataclass
class RecentEventResult:
    id: str
    type: str
    message: str
    created_at: datetime


@dataclass
class DashboardResult:
    stats: DashboardStatsResult
    recent_applications: list[RecentApplicationResult]
    recent_events: list[RecentEventResult]