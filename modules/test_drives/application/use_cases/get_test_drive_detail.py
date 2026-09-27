from modules.test_drives.application.results.get_test_drive_detail_result import (
    GetTestDriveDetailsResult,
)
from modules.test_drives.domain.exceptions import TestDriveNotFound
from modules.auth.domain.exceptions import Unauthorized
from modules.auth.domain.enums import UserRole


class GetTestDriveDetailUseCase:
    """
    Récupère le détail d'un essai routier après vérification
    des droits d'accès de l'utilisateur et retourne également
    son historique d'événements.
    """
    def __init__(self, repository, event_repository):
        self.repository = repository
        self.event_repository = event_repository

    def execute(
        self,
        test_drive_id: str,
        user_id: str,
        user_role: UserRole,
    ):

        test_drive = self.repository.get_full_by_id(
            test_drive_id
        )

        if test_drive is None:
            raise TestDriveNotFound()

        # =========================
        # CLIENT SECURITY
        # =========================

        if (
            user_role == UserRole.CLIENT
            and test_drive.user_id != user_id
        ):
            raise Unauthorized()

        # =========================
        # EVENTS
        # =========================

        events = self.event_repository.get_by_test_drive_id(
            test_drive_id
        )

        return GetTestDriveDetailsResult(
            test_drive=test_drive,
            events=events,
        )