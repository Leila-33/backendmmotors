from modules.test_drives.application.results.get_my_test_drives_result import (
    GetMyTestDrivesResult,
)


class GetMyTestDrivesUseCase:
    """
    Récupère les demandes d'essai routier associées à l'utilisateur connecté.
    """
    def __init__(self, repository):
        self.repository = repository

    def execute(
        self,
        user_id: str,
    ) -> GetMyTestDrivesResult:

        test_drives = self.repository.get_by_user_id(
            user_id
        )

        return GetMyTestDrivesResult(
            items=test_drives
        )