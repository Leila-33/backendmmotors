from datetime import datetime, timezone
from uuid import uuid4

from modules.core.enums import ApplicationStatus, ReservationStatus
from modules.applications.api.schemas import SaveDraftApplicationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository

from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.services.financing_service import FinancingService

from modules.financing.api.schemas import TradeInEstimateRequest
from modules.financing.domain.services.trade_in_service import TradeInService
from modules.auth.infrastructure.db.user_model import UserModel
from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.core.enums import EventType
from modules.applications.domain.entities.event import Event
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository

class SaveDraftApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        financing_service: FinancingService,
        trade_in_service: TradeInService,
        event_repository: EventRepository
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.financing_service = financing_service
        self.trade_in_service = trade_in_service
        self.event_repository = event_repository


    # =========================
    # MAIN ENTRYPOINT
    # =========================
    def execute(self, dto: SaveDraftApplicationDTO, current_user: UserModel
):

        # =========================
        # 1. CREATE OR UPDATE APPLICATION
        # =========================
        if dto.id:
            application = self.application_repository.get_by_id(dto.id)
        else:
            application = self.application_repository.create_base(
                id=str(uuid4()),
                user_id=current_user.id,
                vehicle_id=dto.vehicle_id,
                status=ApplicationStatus.DRAFT,
                created_at=datetime.now(timezone.utc)
            )
            event_type = EventType.APPLICATION_CREATED
            message = "Brouillon du dossier créé"

        # =========================
        # 2. TRADE-IN ESTIMATION (OPTIONAL)
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

            trade_in_value = self.trade_in_service.estimate(trade_request)

            # snapshot persistence
            self.application_repository.save_trade_in(
                application_id=application.id,
                trade_in_value=trade_in_value,
                data=dto.trade_in
            )

        # =========================
        # 3. FINANCING CALCULATION
        # =========================
        total_price = dto.total_price
        if dto.financing is not None:
            financing_result = self.financing_service.calculate(
                FinancingRequest(
                    total_price=total_price,
                    down_payment=dto.financing.down_payment,
                    duration_months=dto.financing.duration_months,
                    trade_in_value=trade_in_value
                )
            )
            financing_snapshot = ApplicationFinancing(
            down_payment=dto.financing.down_payment,
            duration_months=dto.financing.duration_months,
            financed_amount=financing_result.financed_amount,
            monthly_payment=financing_result.monthly_payment
    )

            # snapshot persistence
            self.application_repository.save_financing(
                application_id=application.id,
                data=financing_snapshot
            )

        # =========================
        # 4. UPDATE CORE APPLICATION
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



        # =========================
        # OPTIONS (MANY-TO-MANY SNAPSHOT)
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


        # =========================
        # RESERVATION (RENT ONLY)
        # =========================
        if (
            dto.application_type == "rent"
            and dto.selected_dates
        ):

            self.reservation_repository.create_or_update(
                application_id=application.id,
                vehicle_id=application.vehicle_id,
                start_date=dto.selected_dates.start,
                end_date=dto.selected_dates.end,
                status=ReservationStatus.DRAFT
            )

        event = Event(
            id=str(uuid4()),
            application_id=application.id,
            type=event_type,
            message=message,
            user_id=current_user.id,
            created_at=datetime.now(timezone.utc)
        )

        self.event_repository.save(event)


        self.application_repository.update(application)
        self.application_repository.commit()

        # =========================
        # 5. RETURN
        # =========================
        return application