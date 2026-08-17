from dataclasses import dataclass


@dataclass
class ReconditioningAnalysisResult:

    tasks: list[str]
    cost: float
    duration_days: int