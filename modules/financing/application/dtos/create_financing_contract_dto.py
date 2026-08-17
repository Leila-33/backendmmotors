from dataclasses import dataclass


@dataclass(frozen=True)
class CreateFinancingContractDTO:

    application_id: str