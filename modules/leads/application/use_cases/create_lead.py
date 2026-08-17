import logging
import uuid
from datetime import datetime, timezone

from modules.leads.application.dtos.create_lead_dto import CreateLeadDTO
from modules.leads.application.results.create_lead_result import (
    CreateLeadResult,
)
from modules.leads.domain.entities.lead import Lead
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import ActiveLeadAlreadyExists
from modules.applications.domain.enums import EventType


logger = logging.getLogger(__name__)


class CreateLeadUseCase:

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
        dto: CreateLeadDTO,
    ) -> CreateLeadResult:

        try:

            # =========================
            # BUSINESS RULE
            # =========================

            existing = (
                self.lead_repository
                .find_active_by_user_or_email_and_vehicle(
                    user_id=dto.user_id,
                    email=dto.email,
                    vehicle_id=dto.vehicle_id,
                )
            )

            if existing:
                raise ActiveLeadAlreadyExists()

            # =========================
            # CREATE DOMAIN ENTITY
            # =========================

            lead = Lead(
                id=str(uuid.uuid4()),
                vehicle_id=dto.vehicle_id,
                user_id=dto.user_id,

                first_name=dto.first_name,
                last_name=dto.last_name,

                email=dto.email,
                phone=dto.phone,
                message=dto.message,

                status=LeadStatus.NEW,
                assigned_to=None,

                created_at=datetime.now(timezone.utc),
            )

            # =========================
            # PERSISTENCE
            # =========================

            self.lead_repository.save(lead)

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.LEAD_CREATED,
                message="Nouveau lead créé",
                user_id=dto.user_id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                event_metadata={
                    "lead_id": lead.id,
                    "email": lead.email,
                    "status": lead.status.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Lead créé",
                extra={
                    "lead_id": lead.id,
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateLeadResult(
                lead_id=lead.id,
                status=lead.status.value,
                message="Lead créé avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création lead",
                extra={
                    "user_id": dto.user_id,
                    "vehicle_id": dto.vehicle_id,
                },
            )

            raise