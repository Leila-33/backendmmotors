from dataclasses import dataclass

@dataclass(frozen=True)
class SalesNotificationCountsResult:
    new_leads_count: int
    my_leads_count: int