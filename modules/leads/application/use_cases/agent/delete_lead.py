from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadCannotBeDeleted

)
from modules.leads.domain.enums import LeadStatus

class DeleteLeadUseCase:

    def __init__(
        self,
        lead_repository,
        quote_repository,
        lead_authorization,
        unit_of_work,
    ):
        self.lead_repository = lead_repository
        self.quote_repository = quote_repository
        self.lead_authorization = lead_authorization
        self.unit_of_work = unit_of_work

    def execute(
        self,
        lead_id: str,
        agent_id: str,
    ):

        try:

            lead = self.lead_repository.find_by_id(
    lead_id
)

            if lead is None:
                raise LeadNotFound()

            self.lead_authorization.check_owner(
                lead,
                agent_id,
            )

            if lead.status not in (
                LeadStatus.NEW,
                LeadStatus.ASSIGNED,
                LeadStatus.CONTACTED,
            ):
                raise LeadCannotBeDeleted()

            # Le lead ne doit avoir aucun devis
            if self.quote_repository.has_any_quote(
                lead.id
            ):
                raise LeadCannotBeDeleted()

            self.lead_repository.delete(
                lead.id
            )

            self.unit_of_work.commit()


        except Exception:

            self.unit_of_work.rollback()

            raise