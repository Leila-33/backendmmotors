from modules.leads.domain.exceptions import LeadNotFound
from modules.leads.domain.enums import LeadStatus

from modules.leads.application.dtos.agent.get_lead_detail_dto import (
    GetLeadDetailDTO,
)

from modules.leads.application.results.agent.get_lead_detail_result import (
    GetLeadDetailResult,
)


class GetLeadDetailUseCase:

    def __init__(
        self,
        lead_repository,
        quote_repository,
    ):
        self.lead_repository = lead_repository
        self.quote_repository = quote_repository

    def execute(
        self,
        dto: GetLeadDetailDTO,
    ) -> GetLeadDetailResult:

        # =========================
        # GET LEAD
        # =========================

        lead = (
            self.lead_repository
            .get_by_id_with_details(
                dto.lead_id
            )
        )

        if lead is None:
            raise LeadNotFound()

        # =========================
        # QUOTES
        # =========================

        quotes = (
            self.quote_repository
            .find_summary_by_lead(
                lead.id
            )
        )

        # =========================
        # CREATE QUOTE
        # =========================

        can_create_quote = not (
            self.quote_repository
            .has_active_quote(
                lead.id
            )
        )

        # =========================
        # DELETE
        # =========================

        can_delete = (
            lead.status
            in (
                LeadStatus.NEW,
                LeadStatus.ASSIGNED,
                LeadStatus.CONTACTED,
            )
            and not self.quote_repository.has_any_quote(
                lead.id
            )
        )

        # =========================
        # RESULT
        # =========================

        return GetLeadDetailResult(
            lead=lead,
            quotes=quotes,
            can_create_quote=can_create_quote,
            can_delete=can_delete,
        )