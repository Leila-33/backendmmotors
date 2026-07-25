from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.storage.infrastrucure.s3_service import S3Service
from core.database.unit_of_work import UnitOfWork

class DeleteVehicle:

    def __init__(
        self,
        repo: VehicleRepository,
        s3_service: S3Service,
        unit_of_work: UnitOfWork,
    ):
        self.repo = repo
        self.s3_service = s3_service
        self.unit_of_work = unit_of_work


    def execute(
        self,
        vehicle_id: str
    ):

        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()


        try:

            # =========================
            # DELETE IMAGES S3
            # =========================
            for key in (vehicle.images or []):
                self.s3_service.delete_file(key)


            # =========================
            # DELETE VEHICLE DB
            # =========================
            self.repo.delete(vehicle_id)


            # =========================
            # COMMIT TRANSACTION
            # =========================
            self.unit_of_work.commit()


        except Exception:
            self.unit_of_work.rollback()
            raise


        return {
            "message": "Véhicule supprimé",
            "vehicle_id": vehicle_id
        }