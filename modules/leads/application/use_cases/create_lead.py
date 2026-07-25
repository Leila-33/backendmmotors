
import uuid
from datetime import datetime, timezone
from modules.leads.api.schemas import CreateLeadResponse
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.entities.lead import Lead
from modules.leads.domain.exceptions import ActiveLeadAlreadyExists


class CreateLeadUseCase:

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
        request,
        user_id: str | None = None,
    ):

        try:

            # =========================
            # BUSINESS RULE
            # =========================

            existing = (
                self.lead_repository
                .find_active_by_user_or_email_and_vehicle(
                    user_id=user_id,
                    email=request.email,
                    vehicle_id=request.vehicle_id,
                )
            )

            if existing:
                raise ActiveLeadAlreadyExists()

            # =========================
            # CREATE LEAD
            # =========================

            lead = Lead(

                id=str(uuid.uuid4()),

                vehicle_id=request.vehicle_id,

                user_id=user_id,

                first_name=request.first_name,
                last_name=request.last_name,

                email=request.email,
                phone=request.phone,

                message=request.message,

                status=LeadStatus.NEW,

                assigned_to=None,

                created_at=datetime.now(
                    timezone.utc
                ),
            )

            self.lead_repository.save(
                lead
            )

            self.unit_of_work.commit()

        except Exception:

            self.unit_of_work.rollback()

            raise

        return CreateLeadResponse(

            lead_id=lead.id,

            status=lead.status.value,

            message="Lead créé avec succès",
        )