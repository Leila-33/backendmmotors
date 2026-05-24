class GetMyTestDrivesUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, user_id: str):

        test_drives = self.repository.get_by_user_id(user_id)

        return [
            {
                "id": td.id,
                "vehicle_name": f"{td.vehicle.brand} {td.vehicle.model}" if td.vehicle else "",
                "appointment_date": td.appointment_date,
                "status": td.status.value,
                "comment": td.comment,
            }
            for td in test_drives
        ]