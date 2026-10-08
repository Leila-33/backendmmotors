import logging

from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.agent.agent_lead_dto import AgentLeadDTO
from modules.leads.application.results.agent.assign_lead_result import (
    AssignLeadResult,
)
from modules.auth.domain.enums import UserRole

logger = logging.getLogger(__name__)

class AssignLeadUseCase:
    """
    Attribue un lead à un agent après vérification de son existence
    et de son éligibilité à l'attribution.

    L'action est persistée avant de recalculer les compteurs CRM
    et de notifier les agents concernés.
    """

    def __init__(
        self,
        user_repository,
        lead_repository,
        sales_dashboard_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        self.user_repository = user_repository
        self.lead_repository = lead_repository
        self.sales_dashboard_repository = (
            sales_dashboard_repository
        )
        self.notification_service = notification_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto: AgentLeadDTO,
    ) -> AssignLeadResult:

        try:
            # =========================
            # GET LEAD
            # =========================

            lead = self.lead_repository.find_by_id(
                dto.lead_id
            )

            if not lead:
                raise LeadNotFound()

            # =========================
            # DOMAIN RULE
            # =========================

            lead.ensure_assignable()

            lead.assign_to(
                dto.agent_id
            )

            # =========================
            # PERSISTENCE
            # =========================

            self.lead_repository.update(
                lead
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.LEAD_ASSIGNED,
                message="Lead assigné à un agent",
                user_id=dto.agent_id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                event_metadata={
                    "assigned_to": dto.agent_id,
                    "status": lead.status.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Lead attribué à un agent",
                extra={
                    "lead_id": dto.lead_id,
                    "agent_id": dto.agent_id,
                },
            )

            # =====================================================
            # MISE À JOUR DES COMPTEURS CRM
            # =====================================================

            counts = (
                self.sales_dashboard_repository
                .get_notification_counts(
                    agent_id=dto.agent_id,
                )
            )

            # =====================================================
            # COMPTEUR PERSONNEL
            # =====================================================

            await self.notification_service.send_update(
                user_id=dto.agent_id,
                payload={
                    "type": "MY_LEADS_UPDATED",
                    "count": counts.my_leads_count,
                },
            )

            # =====================================================
            # COMPTEUR GLOBAL
            # =====================================================

            sales_agents = (
                self.user_repository.get_by_role(
                    UserRole.SALES_AGENT,
                )
            )

            for agent in sales_agents:
                await self.notification_service.send_update(
                    user_id=str(agent.id),
                    payload={
                        "type": "NEW_LEADS_UPDATED",
                        "count": counts.new_leads_count,
                    },
                )

        except Exception:
            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de l'attribution du lead",
                extra={
                    "lead_id": dto.lead_id,
                    "agent_id": dto.agent_id,
                },
            )

            raise

        return AssignLeadResult(
            id=lead.id,
            status=lead.status.value,
            assigned_to=lead.assigned_to,
            message="Lead assigné",
        )