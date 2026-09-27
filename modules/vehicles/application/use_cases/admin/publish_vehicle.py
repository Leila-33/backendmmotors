import logging

from modules.vehicles.domain.exceptions import (
    VehicleNotFound,
    VehicleAlreadyPublished,
    VehicleNotReadyForPublication,
)
from modules.vehicles.domain.enums import VehicleStatus
from modules.applications.domain.enums import EventType

from modules.vehicles.application.dtos.admin.vehicle_admin_action_dto import (
    VehicleAdminActionDTO,
)
from modules.vehicles.application.results.admin.publish_vehicle_result import (
    PublishVehicleResult,
)


logger = logging.getLogger(__name__)


class PublishVehicleUseCase:
    """
    Publie un véhicule après vérification qu'il est prêt
    à être mis en ligne.

    La publication met à jour son état et enregistre l'action
    dans l'historique des événements.
    """
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
        dto: VehicleAdminActionDTO,
    ) -> PublishVehicleResult:

        try:

            # =========================
            # GET VEHICLE
            # =========================

            vehicle = self.vehicle_repository.get_by_id(
                dto.vehicle_id
            )

            if vehicle is None:
                raise VehicleNotFound()

            # =========================
            # BUSINESS RULES
            # =========================

            if vehicle.status == VehicleStatus.PUBLISHED:
                raise VehicleAlreadyPublished()

            if vehicle.status != VehicleStatus.READY:
                raise VehicleNotReadyForPublication()

            # =========================
            # DOMAIN TRANSITION
            # =========================

            vehicle.publish()

            # =========================
            # PERSISTENCE
            # =========================

            self.vehicle_repository.update(vehicle)

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.VEHICLE_PUBLISHED,
                message="Véhicule publié",
                vehicle_id=vehicle.id,
                user_id=dto.admin_id,
                event_metadata={
                    "status": vehicle.status.value,
                },
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            logger.info(
                "Véhicule publié",
                extra={
                    "vehicle_id": vehicle.id,
                    "admin_id": dto.admin_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return PublishVehicleResult(
                vehicle_id=vehicle.id,
                status=vehicle.status.value,
                message="Véhicule publié",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur publication véhicule",
                extra={
                    "vehicle_id": dto.vehicle_id,
                    "admin_id": dto.admin_id,
                },
            )

            raise