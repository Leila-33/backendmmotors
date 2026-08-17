# modules/financing/application/dtos/handle_invoice_created_dto.py

from dataclasses import dataclass


@dataclass(frozen=True)
class HandleInvoiceCreatedDTO:

    invoice_id: str
    subscription_id: str