from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadCannotBeDeleted

)
from modules.leads.domain.enums import LeadStatus
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

class DeleteLeadUseCase:

    def __init__(
        self,
        lead_repository,
        quote_repository,
        lead_authorization,
        event_service,
        unit_of_work,
    ):
        self.lead_repository = lead_repository
        self.quote_repository = quote_repository
        self.lead_authorization = lead_authorization
        self.event_service = event_service
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

            self.event_service.log(
                            type=EventType.LEAD_DELETED,
                            message="Lead supprimé",
                            user_id=agent_id,
                            lead_id=lead.id,
                            event_metadata={
                                "email": lead.email,
                                "status": lead.status.value,
                            }
                        )
            
            self.unit_of_work.commit()

            logger.info(
    "Lead supprimé",
    extra={
        "lead_id": lead.id,
        "user_id": agent_id,
    }
)


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
        "Erreur suppression lead",
        extra={
            "lead_id": lead_id,
        }
    )

            raise