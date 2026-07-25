from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from modules.payments.domain.enums import InstallmentStatus


@dataclass
class InstallmentPayment:

    id: str

    financing_contract_id: str

    amount: float

    due_date: datetime
    
    installment_number: int

    status: InstallmentStatus = InstallmentStatus.PENDING

    paid_at: Optional[datetime] = None

    stripe_invoice_id: Optional[str] = None

    created_at: Optional[datetime] = None