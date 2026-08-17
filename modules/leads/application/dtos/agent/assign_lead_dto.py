# modules/leads/application/dto/assign_lead_dto.py

from dataclasses import dataclass


@dataclass
class AssignLeadDTO:
    lead_id: str
    agent_id: str