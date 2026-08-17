from dataclasses import dataclass


@dataclass(frozen=True)
class FinancingInput:
    total_price: float
    down_payment: float
    duration_months: int
    trade_in_value: float = 0