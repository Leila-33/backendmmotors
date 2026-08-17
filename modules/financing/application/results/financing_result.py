from dataclasses import dataclass


@dataclass(frozen=True)
class FinancingResult:
    financed_amount: float
    monthly_payment: float