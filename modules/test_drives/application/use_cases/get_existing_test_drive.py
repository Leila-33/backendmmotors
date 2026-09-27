from modules.test_drives.application.dtos.get_existing_test_drive_dto import GetExistingTestDriveDTO

class GetExistingTestDriveUseCase:
    """
    Récupère la demande d'essai routier existante d'un utilisateur
    pour un véhicule donné.
    """
    def __init__(
        self,
        repository,
    ):
        self.repository = repository

    # =====================================================
    # EXÉCUTION
    # =====================================================

    def execute(
        self,
        dto: GetExistingTestDriveDTO,
    ):

        return self.repository.get_existing_for_user_vehicle(
            user_id=dto.user_id,
            vehicle_id=dto.vehicle_id,
        )