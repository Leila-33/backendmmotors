from dataclasses import dataclass


@dataclass
class ApplicationFinancing:

    down_payment: float

    duration_months: int

    financed_amount: float

    monthly_payment: float