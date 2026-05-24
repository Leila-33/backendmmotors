from modules.core.exceptions import TestDriveNotFound, Unauthorized
class GetTestDriveDetailClientUseCase:

    def __init__(
        self,
        repository,
        event_repository
    ):
        self.repository = repository
        self.event_repository = event_repository

    def execute(self, test_drive_id: str, user_id: str):

        # =========================
        # GET TEST DRIVE
        # =========================
        test_drive = self.repository.get_by_id(test_drive_id)

        if not test_drive:
            raise TestDriveNotFound()

        # sécurité
        if test_drive.user_id != user_id:
            raise Unauthorized()

        # =========================
        # EVENTS TIMELINE
        # =========================
        events = self.event_repository.get_by_test_drive_id(test_drive_id)

        # =========================
        # RESPONSE DTO (Stripe style)
        # =========================
        return {
            "id": test_drive.id,

            "vehicle": {
                "brand": test_drive.vehicle.brand,
                "model": test_drive.vehicle.model,
                "images": test_drive.vehicle.images,
            },

            "appointment_date": test_drive.appointment_date,
            "status": test_drive.status.value,

            "comment": test_drive.comment,

            "user": {
                "id": test_drive.user.id,
                "name": f"{test_drive.user.first_name} {test_drive.user.last_name}",
                "email": test_drive.user.email,
            },

            "timeline": [
                {
                    "type": e.type.value,
                    "message": e.message,
                    "date": e.created_at,
                    "metadata": e.event_metadata,
                }
                for e in events
            ]
        }