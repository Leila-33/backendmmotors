from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone

from modules.warranties.domain.exceptions import VehicleWarrantyNotAssigned, WarrantyPlanNotFound
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

from modules.warranties.domain.exceptions import (
    VehicleWarrantyNotAssigned,
    WarrantyPlanNotFound,
)


class ActivateVehicleWarrantyUseCase:

    def __init__(
        self,
        warranty_plan_repo,
    ):

        self.warranty_plan_repo = (
            warranty_plan_repo
        )

    def execute(
        self,
        vehicle,
        mileage: int | None = None,
    ):

        # =========================
        # WARRANTY
        # =========================
        warranty = vehicle.warranty

        if warranty is None:
            raise VehicleWarrantyNotAssigned()

        # =========================
        # ALREADY ACTIVE
        # =========================
        if warranty.is_active:
            return warranty

        # =========================
        # WARRANTY PLAN
        # =========================
        plan = self.warranty_plan_repo.get_by_id(
            warranty.warranty_plan_id
        )

        if plan is None:
            raise WarrantyPlanNotFound()

        # =========================
        # COMPUTE DATES
        # =========================
        start_date = datetime.now(
            timezone.utc
        )

        end_date = start_date + relativedelta(
            months=plan.duration_months
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

        return warranty