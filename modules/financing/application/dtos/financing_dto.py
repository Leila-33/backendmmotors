from dataclasses import dataclass


@dataclass(frozen=True)
class FinancingDTO:
    total_price: float
    down_payment: float
    trade_in_value: float
    duration_months: int