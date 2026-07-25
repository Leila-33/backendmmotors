from modules.leads.api.schemas import AssignLeadResponse

from modules.leads.domain.exceptions import (
    LeadNotFound
)



class AssignLeadUseCase:

    def __init__(
        self,
        lead_repository,
        unit_of_work,
    ):

        self.lead_repository = (
            lead_repository
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


            self.unit_of_work.commit()


        except Exception:

            self.unit_of_work.rollback()

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
            