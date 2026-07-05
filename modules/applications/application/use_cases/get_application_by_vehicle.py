from modules.auth.infrastructure.db.user_model import UserModel
from modules.applications.domain.repositories.application_repository import ApplicationRepository

class GetApplicationByVehicleUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository
    ):
        self.application_repository = application_repository

    def execute(
        self,
        vehicle_id: str,
        current_user: UserModel
    ):

        return (
            self.application_repository
            .find_active_by_user_and_vehicle(
                user_id=current_user.id,
                vehicle_id=vehicle_id
            )
        )