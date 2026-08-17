# modules/leads/application/results/delete_lead_result.py

from dataclasses import dataclass


@dataclass
class DeleteLeadResult:
    lead_id: str
    message: str