from modules.vehicles.domain.repositories.vehicle_repository import VehicleRepository
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.storage.infrastrucure.s3_service import S3Service
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
from modules.vehicles.api.schemas import DeleteVehicleResponse
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
        current_admin,
    ) -> DeleteVehicleResponse:

        vehicle = self.repo.get_by_id(vehicle_id)

        if not vehicle:
            raise VehicleNotFound()

        try:

            # =====================================================
            # CHECK BUSINESS HISTORY
            # =====================================================

            has_business_history = (
                bool(vehicle.applications)
                or bool(vehicle.reservations)
                or bool(vehicle.test_drives)
                or bool(vehicle.warranty)
                or bool(vehicle.reconditioning)
                or bool(vehicle.inspections)
                or bool(vehicle.leads)
                or bool(vehicle.events)
            )

            # =====================================================
            # ARCHIVE
            # =====================================================

            if has_business_history:

                vehicle.archive()

                self.repo.update(vehicle)

                self.event_service.log(
                    type=EventType.VEHICLE_ARCHIVED,
                    message="Véhicule archivé",
                    vehicle_id=vehicle.id,
                    user_id=current_admin.id,
                    event_metadata={
                        "brand": vehicle.brand,
                        "model": vehicle.model,
                        "reason": "business_history",
                    },
                )

                self.unit_of_work.commit()

                logger.info(
                    "Véhicule archivé",
                    extra={
                        "vehicle_id": vehicle.id,
                        "admin_id": current_admin.id,
                    },
                )

                return DeleteVehicleResponse(
                    vehicle_id=vehicle.id,
                    action="ARCHIVED",
                    message="Véhicule archivé",
                )

            # =====================================================
            # HARD DELETE
            # =====================================================

            for key in (vehicle.images or []):
                self.s3_service.delete_file(key)

            self.repo.delete(vehicle_id)

            self.unit_of_work.commit()

            logger.info(
                "Véhicule supprimé définitivement",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": current_admin.id,
                },
            )

            return DeleteVehicleResponse(
                vehicle_id=vehicle.id,
                action="DELETED",
                message="Véhicule supprimé définitivement",
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