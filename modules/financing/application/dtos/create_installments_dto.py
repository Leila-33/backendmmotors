from dataclasses import dataclass


@dataclass(frozen=True)
class CreateInstallmentsDTO:

    contract_id: str