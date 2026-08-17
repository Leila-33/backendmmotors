from dataclasses import dataclass


@dataclass(frozen=True)
class TradeInEstimateResult:
    estimated_value: float