# modules/financing/application/results/handle_subscription_payment_result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class HandleSubscriptionPaymentResult:

    installment_id: str
    status: str
    invoice_id: str
    message: str