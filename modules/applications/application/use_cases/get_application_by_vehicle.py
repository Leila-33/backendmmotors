from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.entities.application import Application
from modules.applications.application.dtos.vehicle_id_dto import VehicleIdDTO

class GetApplicationByVehicleUseCase:
    """
    Récupère le dossier actif d'un utilisateur pour un véhicule donné.
    """
    def __init__(
        self,
        application_repository: ApplicationRepository,
    ):
        self.application_repository = application_repository

    def execute(
        self,
        dto: VehicleIdDTO,
        current_user_id: str,
    ) -> Application | None:

        return self.application_repository.find_active_by_user_and_vehicle(
            user_id=current_user_id,
            vehicle_id=dto.vehicle_id,
        )