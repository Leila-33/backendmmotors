from dataclasses import dataclass


@dataclass(frozen=True)
class HandlePaymentSuccessResult:

    payment_id: str
    status: str
    vehicle_type: str
    application_id: str
    message: str