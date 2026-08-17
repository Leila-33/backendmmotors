# modules/leads/application/dto/get_lead_detail_dto.py

from pydantic import BaseModel


class GetLeadDetailDTO(BaseModel):
    lead_id: str