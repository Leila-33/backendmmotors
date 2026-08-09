from modules.vehicles.domain.exceptions import VehicleAvailabilityAlreadySet, VehicleNotFound
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
import logging

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
        vehicle_id: str,
        value: bool,
        current_admin
    ):

        # =========================
        # 1. GET VEHICLE
        # =========================
        vehicle = self.vehicle_repository.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()


        # =========================
        # 2. NO-OP CHECK
        # =========================
        if vehicle.is_available == value:
            raise VehicleAvailabilityAlreadySet()

        old_value = vehicle.is_available

        # =========================
        # 3. UPDATE DOMAIN
        # =========================
        vehicle.is_available = value


        # =========================
        # 4. SAVE
        # =========================
        try:

            self.vehicle_repository.update(vehicle)

            self.event_service.log(
    type=EventType.VEHICLE_AVAILABILITY_CHANGED,
    message="Disponibilité du véhicule modifiée",
    vehicle_id=vehicle.id,
    user_id=current_admin.id,
    event_metadata={
        "old_value": old_value,
        "new_value": value,
    }
)


            self.unit_of_work.commit()

            logger.info(
    "Disponibilité véhicule modifiée",
    extra={
        "vehicle_id": vehicle.id,
        "admin_id": current_admin.id,
        "old_value": old_value,
        "new_value": value,
    },
)

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur modification disponibilité véhicule",
                extra={
                    "vehicle_id": vehicle_id,
                    "admin_id": current_admin.id,
                },
            )

            raise


        # =========================
        # 5. RETURN DOMAIN
        # =========================
        return vehicle