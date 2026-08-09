from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.storage.infrastrucure.s3_service import S3Service
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class DeleteVehicle:

    def __init__(
        self,
        repo: VehicleRepository,
        s3_service: S3Service,
        event_service,
        unit_of_work: UnitOfWork,
    ):
        self.repo = repo
        self.s3_service = s3_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work


    def execute(
        self,
        vehicle_id: str,
        current_admin
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

            self.event_service.log(
    type=EventType.VEHICLE_DELETED,
    message="Véhicule archivé",
    vehicle_id=vehicle.id,
    user_id=current_admin.id,
    event_metadata={
        "brand": vehicle.brand,
        "model": vehicle.model,
    }
)
            # =========================
            # COMMIT TRANSACTION
            # =========================
            self.unit_of_work.commit()

            logger.info(
    "Véhicule supprimé",
    extra={
        "vehicle_id": vehicle.id,
        "admin_id": current_admin.id,
    },
)

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur suppression véhicule",
                extra={
                    "vehicle_id": vehicle_id,
                    "admin_id": current_admin.id,
                },
            )

            raise


        return {
            "message": "Véhicule supprimé",
            "vehicle_id": vehicle_id
        }