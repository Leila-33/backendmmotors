from modules.leads.domain.exceptions import (
    LeadNotFound
)

from modules.leads.api.schemas import (
    MarkLeadContactedResponse
)
from modules.leads.application.services.LeadAuthorizationService import LeadAuthorizationService
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

class MarkLeadContactedUseCase:

    def __init__(
        self,
        lead_repository,
        authorization,
        event_service,
        unit_of_work,
    ):
        self.lead_repository = (
            lead_repository
        )

        self.authorization = (
            authorization
        )
        self.event_service = event_service
        self.unit_of_work = (
            unit_of_work
        )


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
            # AUTHORIZATION
            # =========================

            self.authorization.check_owner(
                lead,
                agent_id
            )



            # =========================
            # DOMAIN RULE
            # =========================

            lead.mark_as_contacted()



            # =========================
            # PERSISTENCE
            # =========================

            self.lead_repository.update(
                lead
            )
            self.event_service.log(
    type=EventType.LEAD_CONTACTED,
    message="Prospect contacté",
    user_id=agent_id,
    lead_id=lead.id,
    event_metadata={
        "status": lead.status.value,
    }
)

            self.unit_of_work.commit()

            logger.info(
    "Lead marqué comme contacté",
    extra={
        "lead_id": lead.id,
        "user_id": agent_id,
    }
)

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
        "Erreur lors du marquage du lead comme contacté",
        extra={
            "lead_id": lead_id,
            "user_id": agent_id,
        }
    )

            raise



        # =========================
        # RESPONSE
        # =========================

        return MarkLeadContactedResponse(

            id=lead.id,

            status=lead.status.value,

            message=(
                "Prospect marqué comme contacté"
            )

        )


