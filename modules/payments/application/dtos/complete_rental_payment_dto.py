from dataclasses import dataclass


@dataclass(frozen=True)
class CompleteRentalPaymentDTO:

    application_id: str
    payment_id: str