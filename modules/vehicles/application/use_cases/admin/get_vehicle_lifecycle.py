from modules.vehicles.application.results.admin.get_vehicle_lifecycle_result import (
    GetVehicleLifecycleResult,
)


class GetVehicleLifecycleUseCase:
    """
    Récupère les différentes étapes du cycle de vie d'un véhicule,
    notamment son inspection et son reconditionnement.
    """
    def __init__(
        self,
        inspection_repository,
        reconditioning_repository,
    ):
        self.inspection_repository = inspection_repository
        self.reconditioning_repository = (
            reconditioning_repository
        )

    def execute(
        self,
        vehicle_id: str,
    ) -> GetVehicleLifecycleResult:

        inspection = (
            self.inspection_repository
            .get_by_vehicle_id(vehicle_id)
        )

        reconditioning = (
            self.reconditioning_repository
            .get_by_vehicle_id(vehicle_id)
        )

        return GetVehicleLifecycleResult(
            inspection=inspection,
            reconditioning=reconditioning,
        )