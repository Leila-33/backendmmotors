from dataclasses import dataclass


@dataclass(frozen=True)
class CompleteRentalPaymentResult:

    application_id: str
    vehicle_id: str
    rental_started: bool
    message: str