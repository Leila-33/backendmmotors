# modules/leads/application/dto/mark_lead_contacted_dto.py

from pydantic import BaseModel


class MarkLeadContactedDTO(BaseModel):
    lead_id: str
    agent_id: str