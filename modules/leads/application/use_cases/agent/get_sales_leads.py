from modules.leads.application.dtos.agent.get_sales_leads_dto import (
    GetSalesLeadsDTO,
)

from modules.leads.application.results.agent.get_sales_leads_result import (
    GetSalesLeadsResult,
)
from modules.leads.domain.repositories.lead_repository import LeadRepository

class GetSalesLeadsUseCase:

    def __init__(
        self,
        lead_repository: LeadRepository,
    ):
        self.lead_repository = lead_repository

    def execute(
        self,
        dto : GetSalesLeadsDTO,
    ):
        if dto.scope == "my":
            leads = self.lead_repository.find_my_leads(
                dto.user_id
            )

        elif dto.scope == "unassigned":
            leads = self.lead_repository.find_unassigned_leads()

        return GetSalesLeadsResult(
            leads=leads
        )