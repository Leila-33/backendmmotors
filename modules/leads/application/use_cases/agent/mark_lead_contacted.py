import logging

from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType

from modules.leads.application.dtos.agent.mark_lead_contacted_dto import (
    MarkLeadContactedDTO,
)

from modules.leads.application.results.agent.mark_lead_contacted_result import (
    MarkLeadContactedResult,
)


logger = logging.getLogger(__name__)


class MarkLeadContactedUseCase:

    def __init__(
        self,
        lead_repository,
        authorization,
        event_service,
        unit_of_work,
    ):
        self.lead_repository = lead_repository
        self.authorization = authorization
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: MarkLeadContactedDTO,
    ) -> MarkLeadContactedResult:

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
            # AUTHORIZATION
            # =========================

            self.authorization.check_owner(
                lead,
                dto.agent_id,
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

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.LEAD_CONTACTED,
                message="Prospect contacté",
                user_id=dto.agent_id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                event_metadata={
                    "status": lead.status.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Lead marqué comme contacté",
                extra={
                    "lead_id": dto.lead_id,
                    "user_id": dto.agent_id,
                },
            )

            return MarkLeadContactedResult(
                id=lead.id,
                status=lead.status.value,
                message="Prospect marqué comme contacté",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors du marquage du lead comme contacté",
                extra={
                    "lead_id": dto.lead_id,
                    "user_id": dto.agent_id,
                },
            )

            raise

