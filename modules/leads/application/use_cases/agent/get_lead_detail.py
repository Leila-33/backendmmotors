from modules.leads.domain.exceptions import (
    LeadNotFound
)
from modules.leads.domain.enums import LeadStatus

from modules.leads.infrastructure.mappers.lead_mapper import LeadMapper


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
        lead_id: str,
    ):

        lead = (
            self.lead_repository
            .get_by_id_with_details(
                lead_id
            )
        )


        if lead is None:
            raise LeadNotFound()


        quotes = (
        self.quote_repository
        .find_summary_by_lead(
            lead.id
        )
    )
        can_create_quote = not (
    self.quote_repository
    .has_active_quote(
        lead.id
    )
)
        can_delete = (
            lead.status in (
                LeadStatus.NEW,
                LeadStatus.ASSIGNED,
                LeadStatus.CONTACTED,
            )
            and not self.quote_repository.has_any_quote(
                lead.id
            )
        )

        return LeadMapper.to_detail_response(
            lead=lead,
            quotes=quotes,
            can_create_quote=can_create_quote,
            can_delete=can_delete,
        )