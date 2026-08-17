from dataclasses import dataclass


@dataclass(frozen=True)
class CreateLeadResult:
    lead_id: str
    status: str
    message: str