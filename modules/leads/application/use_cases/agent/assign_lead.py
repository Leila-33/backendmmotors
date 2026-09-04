import logging

from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType
from modules.leads.application.dtos.agent.agent_lead_dto import AgentLeadDTO
from modules.leads.application.results.agent.assign_lead_result import (
    AssignLeadResult,
)


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

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur attribution lead",
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