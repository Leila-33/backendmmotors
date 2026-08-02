from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.domain.entities.application import Application
from modules.applications.domain.enums import (
    ApplicationStatus,
    ApplicationType,
)
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.services.financing_service import FinancingService
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.api.schemas import TradeInEstimateRequest
from modules.financing.domain.services.trade_in_service import TradeInService
from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.domain.entities.application_trade_in import ApplicationTradeIn
from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.applications.domain.repositories.application_financing_repository import ApplicationFinancingRepository
from modules.applications.domain.repositories.application_trade_in_repository import ApplicationTradeInRepository
from modules.applications.domain.repositories.application_option_repository import ApplicationOptionRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.application.services.document_sync_service import DocumentSyncService
from modules.financing.domain.exceptions import (
   FinancingAmountNegative
)
from modules.vehicles.domain.exceptions import VehicleNotAvailable
from modules.applications.api.schemas import ApplicationFormResult


class ApplicationFormService:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        trade_in_repository: ApplicationTradeInRepository,
        financing_repository: ApplicationFinancingRepository,
        application_option_repository: ApplicationOptionRepository,
        reservation_repository: ReservationRepository,
        financing_service: FinancingService,
        trade_in_service: TradeInService,
        document_sync_service: DocumentSyncService,
    ):
        # Repositories
        self.application_repository = application_repository
        self.trade_in_repository = trade_in_repository
        self.financing_repository = financing_repository
        self.application_option_repository = application_option_repository
        self.reservation_repository = reservation_repository

        # Domain / application services
        self.financing_service = financing_service
        self.trade_in_service = trade_in_service
        self.document_sync_service = document_sync_service


    # =========================
    # MAIN METHOD
    # =========================

    def save(
        self,
        dto,
        current_user,
    ) -> Application:


        result = self._get_or_create_application(
    dto,
    current_user
)

        application = result.application


        trade_in_value = (
            self._save_trade_in(
                dto,
                application
            )
        )


        self._save_financing(
            dto,
            application,
            trade_in_value
        )


        self._update_snapshot(
            dto,
            application
        )


        self._save_options(
            dto,
            application
        )


        self._save_documents(
            dto,
            application
        )


        self._save_reservation(
            dto,
            application
        )


        self.application_repository.update(
            application
        )


        return ApplicationFormResult(
            application=application,
            is_new=result.is_new,
        )


    # =========================
    # APPLICATION
    # =========================

    def _get_or_create_application(
        self,
        dto,
        current_user
    ) -> ApplicationFormResult:


        # =========================
        # EXISTING APPLICATION
        # =========================

        if dto.id:

            application = (
                self.application_repository.get_by_id(
                    dto.id
                )
            )

            if not application:
                raise ApplicationNotFound()


            return ApplicationFormResult(
                application=application,
                is_new=False,
            )



        # =========================
        # EXISTING DRAFT
        # =========================

        application = (
            self.application_repository
            .find_draft_by_user_and_vehicle(
                user_id=current_user.id,
                vehicle_id=dto.vehicle_id,
            )
        )


        if application:

            return ApplicationFormResult(
                application=application,
                is_new=False,
            )



        # =========================
        # CREATE DRAFT
        # =========================

        application = Application(
            id=str(uuid4()),
            user_id=current_user.id,
            vehicle_id=dto.vehicle_id,
            status=ApplicationStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
        )


        application = (
            self.application_repository
            .create_base(application)
        )


        return ApplicationFormResult(
            application=application,
            is_new=True,
        )



    # =========================
    # TRADE IN
    # =========================

    def _save_trade_in(
        self,
        dto,
        application
    ):

        if not dto.trade_in:
            return 0


        if not dto.trade_in.enabled:
            return 0



        value = self.trade_in_service.estimate(
            TradeInEstimateRequest(
                brand=dto.trade_in.brand,
                model=dto.trade_in.model,
                year=dto.trade_in.year,
                mileage=dto.trade_in.mileage,
                condition=dto.trade_in.condition,
            )
        )


        self.trade_in_repository.save(
            ApplicationTradeIn(
                application_id=application.id,
                brand=dto.trade_in.brand,
                model=dto.trade_in.model,
                year=dto.trade_in.year,
                mileage=dto.trade_in.mileage,
                condition=dto.trade_in.condition,
                estimated_value=value,
            )
        )


        return value



    # =========================
    # FINANCING
    # =========================

    def _save_financing(
        self,
        dto,
        application,
        trade_in_value
    ):


        if not dto.financing:
            return
        if (
            dto.financing
            and dto.total_price is not None
            and (
                dto.financing.down_payment
                + trade_in_value
                > dto.total_price
            )
        ):
            raise FinancingAmountNegative()


        result = self.financing_service.calculate(
            FinancingRequest(
                total_price=dto.total_price,
                down_payment=dto.financing.down_payment,
                duration_months=dto.financing.duration_months,
                trade_in_value=trade_in_value,
            )
        )


        self.financing_repository.save(
            ApplicationFinancing(
                application_id=application.id,
                down_payment=dto.financing.down_payment,
                duration_months=dto.financing.duration_months,
                financed_amount=result.financed_amount,
                monthly_payment=result.monthly_payment,
            )
        )



    # =========================
    # USER SNAPSHOT
    # =========================

    def _update_snapshot(
        self,
        dto,
        application
    ):

        application.first_name = dto.first_name
        application.last_name = dto.last_name
        application.email = dto.email
        application.phone = dto.phone
        application.address = dto.address
        application.birth_date = dto.birth_date

        application.monthly_income = (
            dto.monthly_income
        )

        application.monthly_expenses = (
            dto.monthly_expenses
        )

        application.employment_status = (
            dto.employment_status
        )



    # =========================
    # OPTIONS
    # =========================

    def _save_options(
        self,
        dto,
        application
    ):

        if dto.selected_option_ids is None:
            return


        self.application_option_repository.replace_options(
            application_id=application.id,
            option_ids=dto.selected_option_ids,
        )



    # =========================
    # DOCUMENTS
    # =========================

    def _save_documents(
        self,
        dto,
        application
    ):

        if dto.documents is None:
            return


        self.document_sync_service.sync(
            application_id=application.id,
            documents=dto.documents,
        )



    # =========================
    # RESERVATION DRAFT
    # =========================

    def _save_reservation(
        self,
        dto,
        application
    ):


        if (
            dto.application_type != ApplicationType.RENT
            or not dto.selected_dates
        ):
            return



        overlapping = (
            self.reservation_repository.exists_overlap(
                vehicle_id=application.vehicle_id,
                start_date=dto.selected_dates.start,
                end_date=dto.selected_dates.end,
                exclude_application_id=application.id,
            )
        )


        if overlapping:
            raise VehicleNotAvailable()



        self.reservation_repository.create_or_update(
            application_id=application.id,
            vehicle_id=application.vehicle_id,
            start_date=dto.selected_dates.start,
            end_date=dto.selected_dates.end,
            status=ReservationStatus.DRAFT,
        )