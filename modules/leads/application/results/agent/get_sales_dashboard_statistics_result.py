from dataclasses import dataclass

@dataclass(frozen=True)
class SalesDashboardStatisticsResult:
    new_leads: int
    my_leads: int
    quotes_sent: int
    applications: int
    unassigned: int
    won: int
    lost: int
    conversion_rate: float