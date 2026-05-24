from modules.test_drives.api.schemas import TestDriveAdminDTO

class GetTestDrivesAdminUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self):

        test_drives = self.repository.get_all()

        return [
            TestDriveAdminDTO(
                id=td.id,
                user_id=td.user_id,
                user_name=f"{td.user.first_name} {td.user.last_name}",
                vehicle_id=td.vehicle_id,
                vehicle_name=f"{td.vehicle.brand} {td.vehicle.model}",
                appointment_date=td.appointment_date,
                status=td.status,
                comment=td.comment,
                created_at=td.created_at
            )
            for td in test_drives
        ]