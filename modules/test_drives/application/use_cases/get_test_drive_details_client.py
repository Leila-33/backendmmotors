from modules.test_drives.domain.exceptions import TestDriveNotFound
from modules.auth.domain.exceptions import Unauthorized

class GetTestDriveDetailClientUseCase:

    def __init__(
        self,
        repository,
        event_repository
    ):
        self.repository = repository
        self.event_repository = event_repository


    def execute(
        self,
        test_drive_id: str,
        user_id: str
    ):

        # =========================
        # GET TEST DRIVE
        # =========================

        test_drive = (
            self.repository
            .get_full_by_id(test_drive_id)
        )


        if not test_drive:
            raise TestDriveNotFound()


        # =========================
        # SECURITY
        # =========================

        if test_drive.user_id != user_id:
            raise Unauthorized()



        # =========================
        # EVENTS
        # =========================

        events = (
            self.event_repository
            .get_by_test_drive_id(test_drive_id)
        )


        # =========================
        # RETURN DATA
        # =========================

        return {
            "test_drive": test_drive,
            "events": events
        }