from modules.financing.domain.exceptions import (
   FinancingAmountNegative
)
from modules.applications.domain.exceptions import ApplicationNotFound, ApplicationAlreadyExists

from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.api.schemas import SubmitApplicationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository

from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.services.financing_service import FinancingService

from modules.financing.api.schemas import TradeInEstimateRequest
from modules.financing.domain.services.trade_in_service import TradeInService
from modules.auth.infrastructure.db.user_model import UserModel
from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.applications.domain.entities.event import Event
from modules.vehicles.domain.exceptions import  VehicleNotAvailable
from modules.applications.api.schemas import SubmitApplicationResponse
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

class SubmitApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        financing_service: FinancingService,
        trade_in_service: TradeInService,
        event_repository: EventRepository,
        reservation_repository: ReservationRepository
    ):
        self.application_repository = application_repository
        self.financing_service = financing_service
        self.trade_in_service = trade_in_service
        self.event_repository = event_repository
        self.reservation_repository = reservation_repository

    # =========================
    # MAIN ENTRYPOINT
    # =========================
    def execute(
        self,
        dto: SubmitApplicationDTO,
        current_user: UserModel
    ):

        # =========================
        # 1. CREATE OR UPDATE APPLICATION
        # =========================
        if dto.id:

            application = (
                self.application_repository
                .get_by_id(dto.id)
            )

            if not application:
                raise ApplicationNotFound()

        else:

            existing = (
                self.application_repository
                .find_active_by_user_and_vehicle(
                    user_id=current_user.id,
                    vehicle_id=dto.vehicle_id
                )
            )

            if existing:
                raise ApplicationAlreadyExists()

            application = (
                self.application_repository
                .create_base(
                    id=str(uuid4()),
                    user_id=current_user.id,
                    vehicle_id=dto.vehicle_id,
                    status=ApplicationStatus.SUBMITTED,
                    created_at=datetime.now(timezone.utc),
                    submitted_at=datetime.now(timezone.utc)
                )
            )

        # =========================
        # 2. TRADE-IN ESTIMATION
        # =========================
        trade_in_value = 0

        if dto.trade_in and dto.trade_in.enabled:

            trade_request = TradeInEstimateRequest(
                brand=dto.trade_in.brand,
                model=dto.trade_in.model,
                year=dto.trade_in.year,
                mileage=dto.trade_in.mileage,
                condition=dto.trade_in.condition
            )

            trade_in_value = (
                self.trade_in_service
                .estimate(trade_request)
            )
        
            if (
                dto.financing
                and dto.financing.down_payment + trade_in_value > dto.total_price
            ):
                raise FinancingAmountNegative()

            self.application_repository.save_trade_in(
                application_id=application.id,
                trade_in_value=trade_in_value,
                data=dto.trade_in
            )

        # =========================
        # 3. FINANCING CALCULATION
        # =========================
        if dto.financing is not None:

            financing_result = (
                self.financing_service.calculate(
                    FinancingRequest(
                        total_price=dto.total_price,
                        down_payment=dto.financing.down_payment,
                        duration_months=dto.financing.duration_months,
                        trade_in_value=trade_in_value
                    )
                )
            )

            financing_snapshot = ApplicationFinancing(
                down_payment=dto.financing.down_payment,
                duration_months=dto.financing.duration_months,
                financed_amount=financing_result.financed_amount,
                monthly_payment=financing_result.monthly_payment
            )

            self.application_repository.save_financing(
                application_id=application.id,
                data=financing_snapshot
            )

        # =========================
        # 4. UPDATE APPLICATION
        # =========================
        application.first_name = dto.first_name
        application.last_name = dto.last_name
        application.email = dto.email
        application.phone = dto.phone
        application.address = dto.address
        application.birth_date = dto.birth_date

        application.monthly_income = dto.monthly_income
        application.monthly_expenses = dto.monthly_expenses
        application.employment_status = dto.employment_status

        application.status = ApplicationStatus.SUBMITTED
        application.submitted_at = datetime.now(timezone.utc)

        # =========================
        # OPTIONS
        # =========================
        if dto.selected_option_ids is not None:

            self.application_repository.replace_options(
                application_id=application.id,
                option_ids=dto.selected_option_ids
            )

        # =========================
        # DOCUMENTS
        # =========================
        if dto.documents is not None:

            self.application_repository.sync_documents(
                application_id=application.id,
                documents=dto.documents
            )

        overlapping = (
            self.reservation_repository.exists_overlap(
                vehicle_id=dto.vehicle_id,
                start_date=dto.selected_dates.start,
                end_date=dto.selected_dates.end
            )
        )

        if overlapping:
            raise VehicleNotAvailable()

        if (
            dto.application_type == "rent"
            and dto.selected_dates
        ):
            self.reservation_repository.create_or_update(
                application_id=application.id,
                vehicle_id=application.vehicle_id,
                start_date=dto.selected_dates.start,
                end_date=dto.selected_dates.end,
                status=ReservationStatus.ACTIVE
            )
        # =========================
        # EVENT
        # =========================
        event = Event(
            id=str(uuid4()),
            application_id=application.id,
            type=EventType.APPLICATION_SUBMITTED,
            message="Dossier soumis avec succès",
            user_id=current_user.id,
            created_at=datetime.now(timezone.utc)
        )

        self.event_repository.save(event)

        # =========================
        # SAVE
        # =========================
        self.application_repository.update(application)
        self.application_repository.commit()

        # =========================
        # RESPONSE
        # =========================
        return SubmitApplicationResponse(
    id=application.id,
    status=application.status,
    message="Dossier soumis avec succès"
)



