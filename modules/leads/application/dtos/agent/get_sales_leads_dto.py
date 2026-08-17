# modules/leads/application/dto/get_sales_leads_dto.py

from pydantic import BaseModel
from typing import Literal


class GetSalesLeadsDTO(BaseModel):
    scope: Literal["my", "unassigned"]
    user_id: str