from dataclasses import dataclass

@dataclass(frozen=True)
class CompleteSalePaymentDTO:
    application_id: str
    payment_id: str