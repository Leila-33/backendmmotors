# modules/financing/application/results/create_installments_result.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateInstallmentsResult:

    contract_id: str
    installment_ids: list[str]
    count: int