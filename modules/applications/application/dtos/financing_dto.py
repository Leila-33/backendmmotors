from dataclasses import dataclass

@dataclass
class FinancingDTO:
    down_payment: float
    duration_months: int