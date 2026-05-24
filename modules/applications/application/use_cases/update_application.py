from modules.core.enums import ApplicationStatus, VehicleOptionType
from modules.applications.api.schemas import UpdateApplicationFullRequest
from datetime import datetime, timezone

from modules.applications.api.schemas import (
    UpdateApplicationResponse
    )

from modules.core.exceptions import (
    NoActiveDraft,
    ApplicationNotModifiable,
    OptionNotAllowed
)

from datetime import datetime, timezone


class UpdateApplicationFull:

    def __init__(
        self,
        repository,
        vehicle_option_repo,
        application_option_repo,
    ):
        self.repository = repository
        self.vehicle_option_repo = vehicle_option_repo
        self.application_option_repo = application_option_repo

    def execute(self, user_id: str, data: UpdateApplicationFullRequest):

        # =========================
        # 1. GET DRAFT
        # =========================
        application = self.repository.get_draft_by_user(user_id)

        if not application:
            raise NoActiveDraft()

        if application.status != ApplicationStatus.DRAFT:
            raise ApplicationNotModifiable()

        # =========================
        # 2. UPDATE FIELDS
        # =========================
        if data.monthly_income is not None:
            application.monthly_income = data.monthly_income

        if data.monthly_expenses is not None:
            application.monthly_expenses = data.monthly_expenses

        if data.employment_status is not None:
            application.employment_status = data.employment_status

        # =========================
        # 3. OPTIONS
        # =========================
        if data.selected_options:

            vehicle_options = self.vehicle_option_repo.get_by_vehicle(application.vehicle_id)

            optional_options = {
                vo.option_id
                for vo in vehicle_options
                if vo.type == VehicleOptionType.OPTIONAL
            }

            # =========================
            # VALIDATION
            # =========================
            for opt_id in data.selected_options:
                if opt_id not in optional_options:
                    raise OptionNotAllowed(opt_id)

            # =========================
            # CLEAN OLD SELECTED OPTIONS
            # =========================
            self.application_option_repo.delete_selected_by_application(application.id)

            # =========================
            # INSERT NEW SELECTED
            # =========================
            for opt_id in data.selected_options:
                self.application_option_repo.create(
                    application_id=application.id,
                    option_id=opt_id,
                )

        # =========================
        # 4. SAVE APPLICATION
        # =========================
        application.updated_at = datetime.now(timezone.utc)
        self.repository.update(application)

        # =========================
        # 5. RESPONSE
        # =========================
        return UpdateApplicationResponse(
            id=application.id,
            status=application.status.value,
            selected_options=data.selected_options or [],
            message="Application mise à jour"
        )