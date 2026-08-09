from modules.leads.api.schemas import AssignLeadResponse

from modules.leads.domain.exceptions import (
    LeadNotFound
)
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)


class AssignLeadUseCase:

    def __init__(
        self,
        lead_repository,
        event_service,
        unit_of_work,
    ):
        self.lead_repository = lead_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work


    def execute(
        self,
        lead_id: str,
        agent_id: str,
    ):

        try:

            # =========================
            # GET LEAD
            # =========================

            lead = (
                self.lead_repository
                .find_by_id(
                    lead_id
                )
            )


            if not lead:
                raise LeadNotFound()



            # =========================
            # DOMAIN RULE
            # =========================

            lead.ensure_assignable()


            lead.assign_to(
                agent_id
            )



            # =========================
            # PERSISTENCE
            # =========================

            self.lead_repository.update(
                lead
            )
            
            self.event_service.log(
    type=EventType.LEAD_ASSIGNED,
    message="Lead assigné à un agent",
    user_id=agent_id,
    lead_id=lead.id,
    event_metadata={
        "assigned_to": agent_id,
        "status": lead.status.value,
    }
)

            self.unit_of_work.commit()

            logger.info(
    "Lead attribué à un agent",
    extra={
        "lead_id": lead.id,
        "agent_id": agent_id,
    }
)


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
        "Erreur attribution lead",
        extra={
            "lead_id": lead_id,
            "agent_id": agent_id,
        }
    )

            raise



        # =========================
        # RESPONSE
        # =========================

        return AssignLeadResponse(

            id=lead.id,

            status=lead.status.value,

            assigned_to=lead.assigned_to,

            message="Lead assigné"

        )
            