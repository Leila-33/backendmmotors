# modules/payments/application/results/complete_sale_payment_result.py

from dataclasses import dataclass


@dataclass
class CompleteSalePaymentResult:

    application_id: str
    vehicle_id: str

    warranty_created: bool
    financing_created: bool

    message: str