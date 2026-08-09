
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from modules.warranties.domain.exceptions import (
    VehicleWarrantyNotAssigned,
    WarrantyPlanNotFound,
)
from modules.applications.domain.enums import EventType
from core.exceptions import DomainException


import logging

logger = logging.getLogger(__name__)


class ActivateVehicleWarrantyUseCase:

    def __init__(
        self,
        warranty_repository,
        warranty_plan_repo,
        event_service,
    ):
        self.warranty_repository = warranty_repository
        self.warranty_plan_repo = warranty_plan_repo
        self.event_service = event_service


    def execute(
        self,
        vehicle,
        user_id,
        mileage=None,
    ):

        try:

            # =========================
            # WARRANTY
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
                        "user_id": user_id,
                    }
                )

                return warranty


            # =========================
            # WARRANTY PLAN
            # =========================

            plan = (
                self.warranty_plan_repo
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


            current_mileage = (
                mileage
                if mileage is not None
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


            self.warranty_repository.update(
                warranty
            )


            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                vehicle_id=warranty.vehicle_id,
                user_id=user_id,
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
                },
            )


            # =========================
            # TECHNICAL LOG
            # =========================

            logger.info(
                "Garantie véhicule activée",
                extra={
                    "vehicle_id": vehicle.id,
                    "warranty_id": warranty.id,
                    "warranty_plan_id": plan.id,
                    "user_id": user_id,
                    "current_mileage": current_mileage,
                }
            )


            return warranty


        except DomainException:
            raise

        except Exception:
            logger.exception(
                "Erreur technique activation garantie",
                extra={
                    "vehicle_id": vehicle.id,
                    "user_id": user_id,
                }
            )
            raise