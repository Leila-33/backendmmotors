from modules.test_drives.domain.exceptions import TestDriveNotFound

class GetTestDriveDetailsUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, test_drive_id: str):

        test_drive = (
            self.repository
            .get_full_by_id(test_drive_id)
        )

        if not test_drive:
            raise TestDriveNotFound()

        return test_drive