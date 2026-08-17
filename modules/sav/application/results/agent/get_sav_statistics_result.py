from dataclasses import dataclass

@dataclass
class CategoryStatResult:
    category: str
    count: int


@dataclass
class GetSavStatisticsResult:
    total: int
    closed: int
    last_7_days: int
    last_30_days: int
    category_distribution: list[CategoryStatResult]
    resolution_rate: float