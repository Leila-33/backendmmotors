# modules/financing/application/results/handle_invoice_created_result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class HandleInvoiceCreatedResult:

    installment_id: str
    invoice_id: str
    message: str