# modules/financing/application/results/create_financing_contract_result.py

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateFinancingContractResult:

    contract_id: str
    application_id: str
    financed_amount: Decimal
    monthly_payment: Decimal
    duration_months: int
    remaining_balance: Decimal