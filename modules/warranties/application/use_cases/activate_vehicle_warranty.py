from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
import logging
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
)
from modules.warranties.domain.exceptions import (
    VehicleWarrantyNotAssigned,
    WarrantyPlanNotFound,
)
from modules.applications.domain.enums import EventType
from modules.warranties.application.dtos.activate_vehicle_warranty_dto import (
    ActivateVehicleWarrantyDTO,
)
from core.database.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)


class ActivateVehicleWarrantyUseCase:

    def __init__(
        self,
        vehicle_repository,
        warranty_repository,
        warranty_plan_repository,
        event_service,
        unit_of_work: UnitOfWork,
    ):
        self.vehicle_repository = vehicle_repository
        self.warranty_repository = warranty_repository
        self.warranty_plan_repository = (
            warranty_plan_repository
        )
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: ActivateVehicleWarrantyDTO,
    ):

        try:

            # =========================
            # GET VEHICLE
            # =========================

            vehicle = (
                self.vehicle_repository
                .get_by_id(dto.vehicle_id)
            )

            if vehicle is None:

                raise VehicleNotFound()

            # =========================
            # GET WARRANTY
            # =========================

            warranty = vehicle.warranty

            if warranty is None:
                raise VehicleWarrantyNotAssigned()

            # =========================
            # IDEMPOTENCY
            # =========================

            if warranty.is_active:

                logger.info(
                    "Garantie déjà active",
                    extra={
                        "vehicle_id": vehicle.id,
                        "warranty_id": warranty.id,
                        "user_id": dto.user_id,
                    },
                )

                return warranty

            # =========================
            # GET WARRANTY PLAN
            # =========================

            plan = (
                self.warranty_plan_repository
                .get_by_id(
                    warranty.warranty_plan_id
                )
            )

            if plan is None:
                raise WarrantyPlanNotFound()

            # =========================
            # DATES
            # =========================

            start_date = datetime.now(
                timezone.utc
            )

            end_date = (
                start_date
                + relativedelta(
                    months=plan.duration_months
                )
            )

            # =========================
            # CURRENT MILEAGE
            # =========================

            current_mileage = (
                dto.mileage
                if dto.mileage is not None
                else vehicle.mileage
            )

            # =========================
            # ACTIVATE
            # =========================

            warranty.activate(
                start_date=start_date,
                end_date=end_date,
                current_mileage=current_mileage,
                max_mileage=plan.mileage_limit,
            )

            # =========================
            # PERSIST
            # =========================

            self.warranty_repository.update(
                warranty
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                vehicle_id=vehicle.id,
                user_id=dto.user_id,
                type=EventType.WARRANTY_ACTIVATED,
                message="Garantie activée.",
                event_metadata={
                    "warranty_id": warranty.id,
                    "warranty_plan_id": plan.id,
                    "duration_months": (
                        plan.duration_months
                    ),
                    "max_mileage": (
                        plan.mileage_limit
                    ),
                    "current_mileage": (
                        current_mileage
                    ),
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # LOG
            # =========================

            logger.info(
                "Garantie véhicule activée",
                extra={
                    "vehicle_id": vehicle.id,
                    "warranty_id": warranty.id,
                    "warranty_plan_id": plan.id,
                    "user_id": dto.user_id,
                    "current_mileage": (
                        current_mileage
                    ),
                },
            )

            return warranty

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur activation garantie",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "user_id": dto.user_id,
                },
            )

            raise