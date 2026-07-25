from modules.leads.domain.exceptions import (
    LeadNotFound
)

from modules.leads.api.schemas import (
    MarkLeadContactedResponse
)
from modules.leads.application.services.LeadAuthorizationService import LeadAuthorizationService



class MarkLeadContactedUseCase:

    def __init__(
        self,
        lead_repository,
        authorization,
        unit_of_work,
    ):
        self.lead_repository = (
            lead_repository
        )

        self.authorization = (
            authorization
        )

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


            self.unit_of_work.commit()


        except Exception:

            self.unit_of_work.rollback()

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


