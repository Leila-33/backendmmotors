from datetime import datetime, timezone

from modules.vehicles.domain.enums import VehicleStatus
from modules.test_drives.domain.exceptions import (
    InvalidAvailabilityDate,
)
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
)

from modules.test_drives.application.dtos.get_availability_dto import (
    GetAvailabilityDTO,
)

from modules.test_drives.application.results.get_availability_result import (
    GetAvailabilityResult,
)


class GetAvailabilityUseCase:

    def __init__(
        self,
        repository,
        vehicle_repository,
    ):
        self.repository = repository
        self.vehicle_repository = vehicle_repository

    def execute(
        self,
        dto: GetAvailabilityDTO,
    ) -> GetAvailabilityResult:

        # =========================
        # VEHICLE CHECK
        # =========================

        vehicle = self.vehicle_repository.get_by_id(
            dto.vehicle_id
        )

        if vehicle is None:
            raise VehicleNotFound()

        if vehicle.status != VehicleStatus.PUBLISHED:
            raise VehicleNotAvailableForTestDrive()

        # =========================
        # PAST DATE
        # =========================

        today = datetime.now(
            timezone.utc
        ).date()

        if dto.date < today:
            raise InvalidAvailabilityDate()

        # =========================
        # AVAILABILITY
        # =========================

        data = self.repository.get_day_availability(
            vehicle_id=dto.vehicle_id,
            selected_date=dto.date,
        )

        # =========================
        # RESULT
        # =========================

        return GetAvailabilityResult(
            date=data["date"],
            timezone=data["timezone"],
            available_slots=data["available_slots"],
        )