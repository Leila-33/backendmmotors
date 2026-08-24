import logging

from modules.vehicles.domain.exceptions import (
    VehicleAvailabilityAlreadySet,
    VehicleNotFound,
)
from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
from modules.vehicles.application.dtos.admin.set_availability_dto import (
    SetAvailabilityDTO,
)   
from modules.vehicles.application.results.admin.set_availability_result import (
    SetAvailabilityResult,
)

logger = logging.getLogger(__name__)


class SetAvailabilityUseCase:

    def __init__(
        self,
        vehicle_repository: VehicleRepository,
        event_service,
        unit_of_work: UnitOfWork,
    ):
        self.vehicle_repository = vehicle_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: SetAvailabilityDTO,
    ) -> SetAvailabilityResult:

        vehicle = self.vehicle_repository.get_by_id(
            dto.vehicle_id
        )

        if not vehicle:
            raise VehicleNotFound()

        if vehicle.is_available == dto.value:
            raise VehicleAvailabilityAlreadySet()

        old_value = vehicle.is_available

        try:

            vehicle.is_available = dto.value

            self.vehicle_repository.update(vehicle)

            self.event_service.log(
                type=EventType.VEHICLE_AVAILABILITY_CHANGED,
                message="Disponibilité du véhicule modifiée",
                vehicle_id=vehicle.id,
                user_id=dto.admin_id,
                event_metadata={
                    "old_value": old_value,
                    "new_value": dto.value,
                },
            )

            self.unit_of_work.commit()

            logger.info(
                "Disponibilité véhicule modifiée",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                    "old_value": old_value,
                    "new_value": dto.value,
                },
            )

            return SetAvailabilityResult(
                vehicle_id=vehicle.id,
                status=vehicle.status.value,
                is_available=vehicle.is_available,
                message=(
                    "Véhicule disponible"
                    if vehicle.is_available
                    else "Véhicule indisponible"
                ),
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification disponibilité véhicule",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise