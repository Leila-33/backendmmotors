from datetime import datetime, timezone
from modules.vehicles.domain.enums import VehicleStatus
from modules.test_drives.domain.exceptions import InvalidAvailabilityDate
from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleNotAvailableForTestDrive,
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
        vehicle_id: str,
        date: str,
    ):

        # =========================
        # VEHICLE CHECK
        # =========================
        vehicle = (
            self.vehicle_repository
            .get_by_id(vehicle_id)
        )

        if vehicle is None:
            raise VehicleNotFound()


        if vehicle.status != VehicleStatus.PUBLISHED:
            raise VehicleNotAvailableForTestDrive()


        # =========================
        # DATE PARSING
        # =========================
        try:

            selected_date = (
                datetime.fromisoformat(date)
            )

        except ValueError:

            raise InvalidAvailabilityDate()


        # =========================
        # UTC NORMALIZATION
        # =========================
        if selected_date.tzinfo is None:

            selected_date = selected_date.replace(
                tzinfo=timezone.utc
            )

        else:

            selected_date = selected_date.astimezone(
                timezone.utc
            )


        # =========================
        # PAST DATE
        # =========================
        today = (
            datetime.now(timezone.utc)
            .date()
        )

        if selected_date.date() < today:
            raise InvalidAvailabilityDate()


        # =========================
        # AVAILABILITY
        # =========================
        return (
            self.repository
            .get_day_availability(
                vehicle_id,
                selected_date
            )
        )