import logging

from modules.vehicles.domain.repositories.vehicle_repository import (
    VehicleRepository,
)
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.storage.infrastrucure.s3_service import S3Service
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)
from modules.vehicles.application.results.admin.delete_vehicle_result import (
    DeleteVehicleResult,
)


logger = logging.getLogger(__name__)


class DeleteVehicleUseCase:
    """
    Supprime un véhicule après vérification de son existence.

    Lorsqu'un historique métier existe, le véhicule est archivé
    au lieu d'être supprimé définitivement. Dans le cas contraire,
    ses fichiers associés sont supprimés du stockage S3 avant
    sa suppression définitive.
    """
    def __init__(
        self,
        repository: VehicleRepository,
        s3_service: S3Service,
        event_service,
        unit_of_work: UnitOfWork,
    ):
        self.repository = repository
        self.s3_service = s3_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: VehicleAdminActionDTO,
    ) -> DeleteVehicleResult:

        try:

            # =========================
            # GET VEHICLE
            # =========================

            vehicle = self.repository.get_by_id(
                dto.vehicle_id
            )

            if vehicle is None:
                raise VehicleNotFound()

            # =========================
            # BUSINESS HISTORY
            # =========================

            has_business_history = (
    self.repository.has_business_history(
        vehicle.id
    )
)

            # =========================
            # ARCHIVE
            # =========================

            if has_business_history:

                vehicle.archive()

                self.repository.update(vehicle)

                self.event_service.log(
                    type=EventType.VEHICLE_ARCHIVED,
                    message="Véhicule archivé",
                    vehicle_id=vehicle.id,
                    user_id=dto.admin_id,
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
                        "admin_id": dto.admin_id,
                    },
                )

                return DeleteVehicleResult(
                    vehicle_id=vehicle.id,
                    action="ARCHIVED",
                )

            # =========================
            # HARD DELETE
            # =========================

            for key in vehicle.images or []:
                self.s3_service.delete_file(key)

            self.repository.delete(
                dto.vehicle_id
            )

            self.unit_of_work.commit()

            logger.info(
                "Véhicule supprimé définitivement",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                },
            )

            return DeleteVehicleResult(
                vehicle_id=vehicle.id,
                action="DELETED",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur suppression véhicule",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise