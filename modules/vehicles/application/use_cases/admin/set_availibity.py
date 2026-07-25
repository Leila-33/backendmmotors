from modules.vehicles.domain.exceptions import VehicleAvailabilityAlreadySet, VehicleNotFound
from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from core.database.unit_of_work import UnitOfWork

class SetAvailabilityUseCase:

    def __init__(
        self,
        vehicle_repository: VehicleRepository,
        unit_of_work: UnitOfWork,
    ):
        self.vehicle_repository = vehicle_repository
        self.unit_of_work = unit_of_work


    def execute(
        self,
        vehicle_id: str,
        value: bool
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


        # =========================
        # 3. UPDATE DOMAIN
        # =========================
        vehicle.is_available = value


        # =========================
        # 4. SAVE
        # =========================
        try:

            self.vehicle_repository.update(vehicle)

            self.unit_of_work.commit()

        except Exception:
            self.unit_of_work.rollback()
            raise


        # =========================
        # 5. RETURN DOMAIN
        # =========================
        return vehicle