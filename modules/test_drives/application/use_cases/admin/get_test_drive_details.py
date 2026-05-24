from modules.core.exceptions import TestDriveNotFound

class GetTestDriveDetailsUseCase:

    def __init__(self, repository):
        self.repository = repository

    def execute(self, test_drive_id: str):

        test_drive = self.repository.get_full_by_id(test_drive_id)

        if not test_drive:
            raise TestDriveNotFound()

        return {
            "id": test_drive.id,

            # =========================
            # USER
            # =========================
            "user_name": f"{test_drive.user.first_name} {test_drive.user.last_name}",
            "user_email": test_drive.user.email,

            # =========================
            # VEHICLE
            # =========================
            "vehicle_name": f"{test_drive.vehicle.brand} {test_drive.vehicle.model}",
            "vehicle_price": test_drive.vehicle.price,
            "vehicle_license_plate": test_drive.vehicle.license_plate,


            # =========================
            # APPOINTMENT
            # =========================
            "appointment_date": test_drive.appointment_date,
            "status": test_drive.status.value,
            "comment": test_drive.comment,

            # =========================
            # EVENTS (TIMELINE)
            # =========================
            "events": [
                {
                    "id": e.id,
                    "type": e.type.value,
                    "message": e.message,
                    "created_at": e.created_at
                }
                for e in test_drive.events
            ]
        }