from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.application.results.application_form_result import (
    ApplicationFormResult,
)
from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn,
)
from modules.applications.application.services.document_sync_service import (
    DocumentSyncService,
)
from modules.applications.domain.entities.application import (
    Application,
)
from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing,
)
from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn,
)
from modules.applications.domain.enums import (
    ApplicationStatus,
    ApplicationType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.applications.domain.repositories.application_financing_repository import (
    ApplicationFinancingRepository,
)
from modules.applications.domain.repositories.application_option_repository import (
    ApplicationOptionRepository,
)
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)
from modules.applications.domain.repositories.application_trade_in_repository import (
    ApplicationTradeInRepository,
)
from modules.applications.application.services.pricing_calculator import PricingCalculator
from modules.applications.application.services.rental_duration_calculator import RentalDurationCalculator
from modules.auth.domain.exceptions import (
    Forbidden
)
from modules.options.domain.repositories.option_repository import OptionRepository
from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository
)
from modules.vehicles.domain.exceptions import (
    VehicleNotFound
)
from modules.vehicles.domain.enums import VehicleType

from modules.financing.domain.services.financing_service import (
    FinancingService,
)
from modules.financing.domain.services.trade_in_service import (
    TradeInService,
)
from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput
)
from modules.financing.domain.inputs.financing_input import (
    FinancingInput
)
from modules.financing.domain.exceptions import (
    ExpensesGreaterThanIncome
)
from modules.reservations.domain.enums import (
    ReservationStatus,
)
from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)

from modules.vehicles.domain.exceptions import (
    VehicleNotAvailable,
)


class ApplicationFormService:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        vehicle_repository: VehicleRepository,
        trade_in_repository: ApplicationTradeInRepository,
        financing_repository: ApplicationFinancingRepository,
        application_option_repository: ApplicationOptionRepository,
        option_repository: OptionRepository,
        reservation_repository: ReservationRepository,
        financing_service: FinancingService,
        trade_in_service: TradeInService,
        document_sync_service: DocumentSyncService,
        rental_duration_calculator: RentalDurationCalculator,
        pricing_calculator: PricingCalculator
    ):
        # Repositories
        self.application_repository = application_repository
        self.vehicle_repository = vehicle_repository
        self.trade_in_repository = trade_in_repository
        self.financing_repository = financing_repository
        self.application_option_repository = application_option_repository
        self.option_repository = option_repository
        self.reservation_repository = reservation_repository

        # Domain / application services
        self.financing_service = financing_service
        self.trade_in_service = trade_in_service
        self.document_sync_service = document_sync_service
        self.rental_duration_calculator = rental_duration_calculator
        self.pricing_calculator = pricing_calculator

    # =========================
    # MAIN METHOD
    # =========================

    def save(
        self,
        dto,
        current_user_id: str,
    ) -> ApplicationFormResult:

        self._validate_financial_information(dto)

        result = self._get_or_create_application(
            dto,
            current_user_id,
        )

        application = result.application

        # =========================
        # VEHICULE
        # =========================

        vehicle = (
            self.vehicle_repository.get_by_id(
                application.vehicle_id
            )
        )

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # OPTIONS
        # =========================

        options = (
            self.option_repository.get_by_ids(
                dto.selected_option_ids
            )
        )

        # =========================
        # PRICING
        # =========================
        if vehicle.type == VehicleType.RENT:

            rental_days = (
                self.rental_duration_calculator.calculate(
                    start_date=dto.selected_dates.start,
                    end_date=dto.selected_dates.end,
                )
            )

        else:

            rental_days = 1


        pricing = self.pricing_calculator.calculate(
            vehicle=vehicle,
            options=options,
            discount=application.discount or 0,
            rental_days=rental_days,
        )

        application.base_price = (
            pricing.base_price
        )

        application.optional_price = (
            pricing.optional_price
        )

        application.discount = (
            pricing.discount
        )

        application.total_price = (
            pricing.total_price
        )

        # =========================
        # TRADE-IN
        # =========================

        trade_in_value = self._save_trade_in(
            dto,
            application.id,
        )

        # =========================
        # FINANCING
        # =========================

        self._save_financing(
            dto,
            application,
            trade_in_value,
        )

        # =========================
        # AUTRES DONNEES
        # =========================

        self._update_snapshot(
            dto,
            application,
        )

        self._save_options(
            dto,
            application.id,
        )

        self._save_documents(
            dto,
            application.id,
        )

        self._save_reservation(
            dto,
            application,
        )

        # =========================
        # PERSISTANCE
        # =========================

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
        current_user_id: str,
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

            # Vérifie que le dossier appartient bien
            # à l'utilisateur connecté.
            if application.user_id != current_user_id:
                raise Forbidden(
                    "Vous n'êtes pas autorisé à modifier ce dossier."
                )

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
                user_id=current_user_id,
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

            user_id=current_user_id,

            vehicle_id=dto.vehicle_id,

            status=ApplicationStatus.DRAFT,

            # Valeurs tarifaires initiales.
            # Le calcul définitif sera effectué
            # par PricingCalculator.
            base_price=None,
            optional_price=0,
            discount=0,
            total_price=None,

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
        application_id: str,
    ) -> int:

        if not dto.trade_in:
            return 0

        if not dto.trade_in.enabled:
            return 0

        trade_in = dto.trade_in

        trade_in_input = TradeInInput(
            brand=trade_in.brand,
            model=trade_in.model,
            year=trade_in.year,
            mileage=trade_in.mileage,
            condition=trade_in.condition,
        )

        result = self.trade_in_service.estimate(
            trade_in_input
        )

        self.trade_in_repository.save(
            ApplicationTradeIn(
                application_id=application_id,
                brand=trade_in.brand,
                model=trade_in.model,
                year=trade_in.year,
                mileage=trade_in.mileage,
                condition=trade_in.condition,
                estimated_value=result.estimated_value,
            )
        )

        return result.estimated_value

    # =========================
    # FINANCING
    # =========================

    def _save_financing(
        self,
        dto,
        application: Application,
        trade_in_value: float = 0,
    ):
        # =========================
        # VÉRIFICATION
        # =========================

        # Aucun financement demandé.
        if not dto.financing:
            return

        # Le prix total doit avoir été calculé
        # par le PricingCalculator avant cette étape.
        if application.total_price is None:
            return

        # =========================
        # DONNÉES DU FINANCEMENT
        # =========================

        down_payment = float(
            dto.financing.down_payment or 0
        )

        duration_months = int(
            dto.financing.duration_months
        )

        trade_in_value = float(
            trade_in_value or 0
        )

        # =========================
        # CALCUL DU FINANCEMENT
        # =========================

        financing_input = FinancingInput(
            # Prix total du dossier.
            total_price=application.total_price,

            # Apport du client.
            down_payment=down_payment,

            # Durée du financement.
            duration_months=duration_months,

            # Valeur de reprise calculée
            # côté backend.
            trade_in_value=trade_in_value,
        )

        result = self.financing_service.calculate(
            financing_input
        )

        # =========================
        # ENREGISTREMENT
        # =========================

        self.financing_repository.save(
            ApplicationFinancing(
                application_id=application.id,

                down_payment=down_payment,

                duration_months=duration_months,

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
        application_id: str
    ):

        if dto.selected_option_ids is None:
            return


        self.application_option_repository.replace_options(
            application_id=application_id,
            option_ids=dto.selected_option_ids,
        )



    # =========================
    # DOCUMENTS
    # =========================

    def _save_documents(
        self,
        dto,
        application_id: str
    ):

        if dto.documents is None:
            return


        self.document_sync_service.sync(
            application_id=application_id,
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

    def _validate_financial_information(self, dto):

        if (
            dto.monthly_income is not None
            and dto.monthly_expenses is not None
            and dto.monthly_expenses > dto.monthly_income
        ):
            raise ExpensesGreaterThanIncome()