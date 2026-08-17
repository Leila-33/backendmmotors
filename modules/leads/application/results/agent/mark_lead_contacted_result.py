# modules/leads/application/results/mark_lead_contacted_result.py

from dataclasses import dataclass


@dataclass
class MarkLeadContactedResult:
    id: str
    status: str
    message: str