from dataclasses import dataclass


@dataclass
class AssignLeadResult:
    id: str
    status: str
    assigned_to: str
    message: str