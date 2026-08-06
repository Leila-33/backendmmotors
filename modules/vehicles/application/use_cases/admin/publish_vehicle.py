from modules.vehicles.domain.exceptions import VehicleNotFound, VehicleAlreadyPublished, VehicleNotReadyForPublication
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.enums import EventType


class PublishVehicleUseCase:

    def __init__(
        self,
        vehicle_repository,
        event_service,
        unit_of_work,
        
    ):
        self.vehicle_repository = vehicle_repository
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        vehicle_id: str,
        current_admin
    ):

        vehicle = self.vehicle_repository.get_by_id(
            vehicle_id
        )

        if not vehicle:
            raise VehicleNotFound()

        # =========================
        # BUSINESS RULES
        # =========================
        if vehicle.status == VehicleStatus.PUBLISHED:
            raise VehicleAlreadyPublished()

        if vehicle.status != VehicleStatus.READY:
            raise VehicleNotReadyForPublication()

        # =========================
        # DOMAIN
        # =========================
        vehicle.publish()

        # =========================
        # SAVE
        # =========================
        self.vehicle_repository.update(
            vehicle
        )
        self.event_service.log(
    type=EventType.VEHICLE_PUBLISHED,
    message="Véhicule publié",
    vehicle_id=vehicle.id,
    user_id=current_admin.id,
    event_metadata={
        "status": vehicle.status.value
    }
)
        self.unit_of_work.commit()

        return vehicle