# modules/leads/application/dto/delete_lead_dto.py

from pydantic import BaseModel


class DeleteLeadDTO(BaseModel):
    lead_id: str
    agent_id: str