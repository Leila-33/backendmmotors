import logging

from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadCannotBeDeleted,
)

from modules.leads.domain.enums import LeadStatus

from modules.applications.domain.enums import EventType

from modules.leads.application.dtos.agent.agent_lead_dto import (
    AgentLeadDTO,
)

from modules.leads.application.results.agent.delete_lead_result import (
    DeleteLeadResult,
)


logger = logging.getLogger(__name__)


class DeleteLeadUseCase:
    """
    Supprime un lead après vérification des droits de l'agent,
    de son statut et de l'absence de devis associé.

    La suppression est ensuite enregistrée dans l'historique
    des événements.
    """
    def __init__(
        self,
        lead_repository,
        quote_repository,
        lead_authorization,
        sales_dashboard_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        self.lead_repository = lead_repository
        self.quote_repository = quote_repository
        self.lead_authorization = lead_authorization
        self.sales_dashboard_repository = sales_dashboard_repository
        self.notification_service = notification_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto: AgentLeadDTO,
    ) -> DeleteLeadResult:

        try:

            # =========================
            # GET LEAD
            # =========================

            lead = self.lead_repository.find_by_id(
                dto.lead_id
            )

            if lead is None:
                raise LeadNotFound()

            # =========================
            # AUTHORIZATION
            # =========================

            self.lead_authorization.check_owner(
                lead,
                dto.agent_id,
            )

            # =========================
            # BUSINESS RULE
            # =========================

            if lead.status not in (
                LeadStatus.NEW,
                LeadStatus.ASSIGNED,
                LeadStatus.CONTACTED,
            ):
                raise LeadCannotBeDeleted()

            # =========================
            # QUOTE CHECK
            # =========================

            if self.quote_repository.has_any_quote(
                lead.id
            ):
                raise LeadCannotBeDeleted()

            # =========================
            # DELETE
            # =========================

            self.lead_repository.delete(
                lead.id
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.LEAD_DELETED,
                message="Lead supprimé",
                user_id=dto.agent_id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                event_metadata={
                    "email": lead.email,
                    "status": lead.status.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # UPDATE MY LEADS COUNT
            # =========================

            my_leads_count = (
                    self.sales_dashboard_repository
                    .count_my_leads(
                        agent_id=dto.agent_id,
                    )
                )

            await self.notification_service.send_update(
                    user_id=dto.agent_id,
                    payload={
                        "type": "MY_LEADS_UPDATED",
                        "count": my_leads_count,
                    },
                )

            logger.info(
                "Lead supprimé",
                extra={
                    "lead_id": lead.id,
                    "user_id": dto.agent_id,
                },
            )

            return DeleteLeadResult(
                lead_id=lead.id,
                message="Lead supprimé avec succès.",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur suppression lead",
                extra={
                    "lead_id": dto.lead_id,
                    "user_id": dto.agent_id,
                },
            )

            raise