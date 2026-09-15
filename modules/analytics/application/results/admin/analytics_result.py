from dataclasses import dataclass


@dataclass
class ApplicationByDayResult:
    date: str
    count: int


@dataclass
class StatusDistributionResult:
    name: str
    value: int


@dataclass
class RevenueByMonthResult:
    month: str
    amount: float


@dataclass
class AnalyticsStatsResult:
    total: int
    active: int
    rejected: int
    submitted: int
    draft: int


@dataclass
class AnalyticsResult:
    applications_by_day: list[ApplicationByDayResult]
    status_distribution: list[StatusDistributionResult]
    revenue: list[RevenueByMonthResult]
    stats: AnalyticsStatsResult

